#pragma once
#include <math.h>
#include <stdint.h>

// scipy.signal.butter(4, [60, 100], fs=500, btype="bandpass", output="sos").
// Same response as the SZH-GJD001 seller's GJD001_code.ino; not the old game's filter.
static const float SZH_SOS[4][5] = {
    {0.00223489f, 0.00446978f, 0.00223489f, -0.73945727f, 0.59923508f},
    {1.0f, 2.0f, 1.0f, -1.03789224f, 0.64082390f},
    {1.0f, -2.0f, 1.0f, -0.59186255f, 0.80647974f},
    {1.0f, -2.0f, 1.0f, -1.33318587f, 0.85392964f}
};

class SzhGjd001Filter {
    bool useBandpass;
    float state[4][2] = {};
    float squares[20] = {};
    float sum = 0;
    float baseline = 0;
    uint16_t settling = 0;
    uint8_t cursor = 0;
public:
    explicit SzhGjd001Filter(bool bandpass = true): useBandpass(bandpass) {}
    void reset() { *this = SzhGjd001Filter(useBandpass); }

    float update(uint16_t raw) {
        // Start/ZERO while relaxed. Center before filtering to avoid an initial DC transient.
        if (settling < 250) {
            ++settling;
            baseline += (raw-baseline)/settling;
            return 0;
        }
        float value = raw-baseline;
        for (uint8_t i=0; useBandpass && i<4; ++i) {
            const float *c = SZH_SOS[i];
            const float x = value-c[3]*state[i][0]-c[4]*state[i][1];
            value = c[0]*x+c[1]*state[i][0]+c[2]*state[i][1];
            state[i][1] = state[i][0];
            state[i][0] = x;
        }
        // 20 samples = 40 ms at 500 Hz. Keep amplitude in ADC units for the app.
        const float power = value*value;
        sum += power-squares[cursor];
        squares[cursor] = power;
        cursor = (cursor+1)%20;
        return sqrtf(fmaxf(0.0f, sum)/20.0f);
    }
};
