# Design appendix: future unattended control (AAB-PHONE-AGENT-001) - comparison only, no implementation

| | (a) Phone-initiated pull from durable GitHub queue, local allowlist + STOP | (b) Termux:API / narrowly authorised Accessibility, owner opt-in | (c) Persistent cloud-to-phone webhook / tunnel |
|---|---|---|---|
| Background limits | Runs only when owner starts it, or via Termux:Boot/termux-job-scheduler; Android may delay jobs (Doze). Tolerant of delay by design. | Accessibility services survive in background but Android 13+ "restricted settings" and Android 16 add friction; Termux:API calls need the app alive. | Needs a always-listening process; Android kills/throttles it unless a foreground notification + battery exemption is granted. |
| Battery | Low (periodic short pulls). | Medium; Accessibility observes all UI events. | High (open socket, wake locks). |
| OS permissions | None beyond Termux storage of its own files. | Termux:API permissions per feature; Accessibility = full screen read/act - very high privilege. | Foreground service + battery-optimisation exemption; possibly VPN/tunnel app. |
| Auth | Read-only fetch of a queue; commands only from a local allowlist, so a forged queue item can at worst request an allowlisted check. Needs a scoped read credential or public data - design decision for review. | Owner opt-in on device; but any compromise of the controlling path = device control. | Inbound endpoint must be authenticated; exposes the phone to the internet; tunnel credentials to manage. |
| Reliability | Good: queue is durable, missed runs retry next pull; fails closed. | Fragile: UI automation breaks on app updates; Accessibility may be revoked by OS. | Fragile on mobile networks; tunnel drops; free tunnels have limits. |
| Cost | $0 (GitHub free tier, Termux free). | $0 (F-Droid apps). | Often $0 only on limited free tiers; risk of paid upgrade - conflicts with $0 rule. |
| Android-only owner steps | Install Termux (done), later one reviewed script; optionally Termux:Boot. | Install Termux:API, grant each permission, enable Accessibility via restricted-settings flow. | Install tunnel client, grant battery exemption, keep notification. |

**Recommendation: (a)**, phone-initiated pull with a local allowlist and a STOP file/flag. It needs no inbound exposure, no high-privilege Android permission, costs $0, fails closed, and fits Android background limits. (b) and (c) are not recommended for v0.2: (b) grants near-total device control; (c) adds internet exposure and likely cost.

Open questions for reviewer (UNVERIFIED): how the phone authenticates to a private repo without placing a GitHub token in Termux (current owner rule forbids it); Doze delay on the owner's specific Android 16 device. Nothing here is implemented.
