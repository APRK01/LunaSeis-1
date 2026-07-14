# Decision 0023: preserve continuous scan v0.2 as a second negative result

Date: 2026-07-14

Accept the frozen v0.2 comparison without retuning. Robust preprocessing reduces CNN false triggers from 0.9233 to 0.3195 per hour and retention from 62.48% to 45.58%, but remains worse than handcrafted logistic regression at 0.1848 false triggers per hour. Robust CNN, original CNN, logistic, and STA/LTA all recover zero of three eligible events at the primary ±180-second tolerance.

The denominator of three makes event recall descriptive, but it is sufficient to reject any claim that the proposed CNN currently provides operationally useful lunar-event detection or retention. Frame v0.2 is consumed permanently.
