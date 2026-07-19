package com.yourbusiness.formfusion.user

/**
 * Cross-screen holder for the user's display name (entered on HomeScreen, shown on
 * SessionSummaryScreen) — there's no persistent user identity anywhere else in the app,
 * and Screen-enum navigation carries no arguments, so this is the simplest source of truth.
 */
object UserProfile {
    var name: String = ""
}
