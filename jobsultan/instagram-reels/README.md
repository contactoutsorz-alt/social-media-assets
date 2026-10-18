# JobSultan Instagram Reels — upload your existing videos here

**Only upload original clips to [uploads/](uploads/)** using GitHub's **Add file → Upload files**.
Do not upload videos to the JobSultan shared image folder.

When you commit MP4, MOV, M4V or WebM files, GitHub Actions automatically:
1. Checks each source clip is between **3 and 180 seconds**.
2. Exports a portrait **1080×1920 H.264 MP4 without any audio track** (not merely volume set to zero).
3. Keeps the original uploaded video untouched.
4. Places the silent output in [silent/](silent/), and updates [silent/manifest.json](silent/manifest.json).
5. Makes the silent MP4 publicly accessible for the private JobSultan Instagram Buffer autoposter.

Your original clips are retained under uploads. The processor pads rather than crops footage, so landscape video gets black space around it rather than being cut off. Videos are never generated.

GitHub's browser uploader generally limits **individual files to 25 MB**. If a video cannot be uploaded, reduce it first or ask for help rather than trying to upload a ZIP (ZIPs are not auto-processed).

Do not add soundtrack or Instagram music in Buffer; the Reels must stay silent. Any first publication should be confirmed in Instagram.

**Publishing:** JobSultan's morning and lunchtime Instagram slots remain image posts. Its **18:45 Europe/London** slot automatically picks a silent Reel when processed clips exist, cycling through each clip before reusing one. Already queued photo posts are not silently deleted. Until you upload videos, 18:45 keeps posting the existing photo content.
