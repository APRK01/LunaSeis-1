#!/usr/bin/env python3
"""Audit raw Phase 0 MiniSEED timing/gaps and create the first waveform plot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from obspy import UTCDateTime, read

ARRIVALS = {
    "S12": UTCDateTime("1971-07-29T20:59:37.900Z"),
    "S14": UTCDateTime("1971-07-29T20:59:19.500Z"),
}
ORIGIN = UTCDateTime("1971-07-29T20:58:42.900Z")


def load_station(day_root: Path, station: str) -> dict[str, object]:
    station_dir = day_root / station.lower() / "1971" / "210"
    traces = {}
    for path in sorted(station_dir.glob("*.mseed")):
        stream = read(str(path))
        if len(stream) != 1:
            raise RuntimeError(f"Expected one trace in {path}, found {len(stream)}")
        trace = stream[0]
        traces[trace.stats.channel] = trace
    if "ATT" not in traces:
        raise RuntimeError(f"Missing ATT trace for {station}")
    return traces


def att_mapping(att_trace, target: UTCDateTime) -> dict[str, object]:
    values = np.asarray(att_trace.data, dtype=float)
    valid_indices = np.flatnonzero(values != -1.0)
    target_epoch = float(target.timestamp)
    nearest_position = int(np.argmin(np.abs(values[valid_indices] - target_epoch)))
    index = int(valid_indices[nearest_position])
    nominal = att_trace.stats.starttime + index / att_trace.stats.sampling_rate
    att_time = UTCDateTime(values[index])
    return {
        "target_time": str(target),
        "nearest_att_time": str(att_time),
        "nominal_time_at_nearest_att": str(nominal),
        "att_minus_target_seconds": float(att_time - target),
        "nominal_minus_target_seconds": float(nominal - target),
        "att_minus_nominal_seconds": float(att_time - nominal),
    }


def trace_audit(trace, window_start: UTCDateTime, window_end: UTCDateTime) -> dict[str, object]:
    values = np.asarray(trace.data)
    start_index = max(0, int(np.floor((window_start - trace.stats.starttime) * trace.stats.sampling_rate)))
    end_index = min(len(values), int(np.ceil((window_end - trace.stats.starttime) * trace.stats.sampling_rate)) + 1)
    window = values[start_index:end_index]
    sentinel = -1.0 if trace.stats.channel == "ATT" else -1
    return {
        "id": trace.id,
        "start_time": str(trace.stats.starttime),
        "end_time": str(trace.stats.endtime),
        "sample_rate_hz": float(trace.stats.sampling_rate),
        "sample_count": int(trace.stats.npts),
        "sentinel_count_full_day": int(np.count_nonzero(values == sentinel)),
        "sentinel_count_plot_window": int(np.count_nonzero(window == sentinel)),
        "plot_window_sample_count": int(window.size),
    }


def create_plot(stations, output: Path, pre_seconds: float, post_seconds: float) -> None:
    panels = [(station, channel, trace) for station, traces in stations.items()
              for channel, trace in traces.items() if channel != "ATT"]
    fig, axes = plt.subplots(len(panels), 1, figsize=(12, 2.15 * len(panels)), sharex=True)
    if len(panels) == 1:
        axes = [axes]

    for axis, (station, channel, trace) in zip(axes, panels):
        arrival = ARRIVALS[station]
        start = arrival - pre_seconds
        end = arrival + post_seconds
        sliced = trace.slice(start, end, nearest_sample=False)
        values = np.asarray(sliced.data, dtype=float)
        values[values == -1] = np.nan
        seconds = np.arange(values.size) / sliced.stats.sampling_rate + float(sliced.stats.starttime - arrival)
        mapping = att_mapping(stations[station]["ATT"], arrival)
        axis.plot(seconds, values, color="#17324d", linewidth=0.55, rasterized=True)
        axis.axvline(0, color="#d1495b", linewidth=1.2, label="published P arrival")
        axis.axvline(
            mapping["nominal_minus_target_seconds"], color="#e9a23b", linewidth=1.1,
            linestyle="--", label="ATT-mapped published time"
        )
        axis.set_ylabel(f"{station} {channel}\nraw counts")
        axis.grid(axis="x", color="#d8dee6", linewidth=0.5)
        axis.spines[["top", "right"]].set_visible(False)

    axes[0].legend(loc="upper right", frameon=False, ncols=2)
    axes[-1].set_xlabel("Nominal MiniSEED seconds relative to published station P arrival")
    fig.suptitle("LunaSeis-1 Phase 0: Apollo 15 S-IVB impact - unprocessed waveforms", fontsize=15)
    fig.text(
        0.5, 0.012,
        "Raw archive counts; -1 gap sentinels masked only for display. No filtering, detrending, "
        "normalization, interpolation, or response removal.",
        ha="center", fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.035, 1, 0.975))
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--day-root", type=Path,
        default=Path("data/raw/apollo_pse_v1.0/data/xa/continuous_waveform"),
    )
    parser.add_argument(
        "--audit-output", type=Path,
        default=Path("results/predictions/phase0_waveform_audit.json"),
    )
    parser.add_argument(
        "--plot-output", type=Path,
        default=Path("results/figures/phase0_apollo15_sivb_raw_waveforms.png"),
    )
    parser.add_argument("--pre-seconds", type=float, default=120.0)
    parser.add_argument("--post-seconds", type=float, default=480.0)
    args = parser.parse_args()

    stations = {station: load_station(args.day_root, station) for station in ARRIVALS}
    report = {
        "source_bundle": "urn:nasa:pds:apollo_pse::1.0",
        "event": "Apollo 15 S-IVB artificial impact",
        "published_origin_time": str(ORIGIN),
        "processing": "none; raw values audited; -1 sentinels masked only in plot",
        "stations": {},
    }
    for station, traces in stations.items():
        arrival = ARRIVALS[station]
        report["stations"][station] = {
            "published_p_arrival": str(arrival),
            "att_mapping": att_mapping(traces["ATT"], arrival),
            "traces": {
                channel: trace_audit(trace, arrival - args.pre_seconds, arrival + args.post_seconds)
                for channel, trace in sorted(traces.items())
            },
        }

    args.audit_output.parent.mkdir(parents=True, exist_ok=True)
    args.audit_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    create_plot(stations, args.plot_output, args.pre_seconds, args.post_seconds)
    print(f"wrote {args.audit_output}")
    print(f"wrote {args.plot_output}")
    for station, item in report["stations"].items():
        mapping = item["att_mapping"]
        print(
            f"{station}: ATT-published={mapping['att_minus_target_seconds']:+.3f}s; "
            f"nominal-published={mapping['nominal_minus_target_seconds']:+.3f}s"
        )


if __name__ == "__main__":
    main()
