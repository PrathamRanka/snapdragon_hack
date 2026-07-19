package com.yourbusiness.formfusion

import org.junit.Assert.assertEquals
import org.junit.Test

class SessionSummaryScreenTest {

    @Test
    fun `durations under 60 seconds are shown in seconds`() {
        assertEquals("0 s", formatSessionDuration(0))
        assertEquals("45 s", formatSessionDuration(45))
        assertEquals("59 s", formatSessionDuration(59))
    }

    @Test
    fun `durations of 60 seconds or more are shown as minutes and seconds`() {
        assertEquals("1m 00s", formatSessionDuration(60))
        assertEquals("1m 05s", formatSessionDuration(65))
        assertEquals("2m 30s", formatSessionDuration(150))
    }

    @Test
    fun `large durations still format correctly`() {
        assertEquals("10m 00s", formatSessionDuration(600))
    }
}
