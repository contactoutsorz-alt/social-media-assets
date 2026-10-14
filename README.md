# Social Media Assets

Public, reusable media library for our Buffer-powered social posts.

## Current folders

- [JobSultan shared images](jobsultan/shared-images/) — **one copy of every approved picture** for both JobSultan LinkedIn and Instagram. Upload your existing JPG/PNG pictures here.
- [Outsorz LinkedIn](outsorz/linkedin/) — optional dedicated Outsorz LinkedIn visuals.

There is no Outsorz Instagram autoposter. JobSultan Instagram and LinkedIn have independent captions, schedules and state, but reference the **same physical media files**.

## Upload instructions

1. Open [jobsultan/shared-images](jobsultan/shared-images/).
2. Click **Add file → Upload files**, select your existing images, and commit them to `main`.
3. Give each image a descriptive, stable filename, such as `job-search-001.jpg` or `hiring-tips-001.png`.
4. Link that filename to both posting configurations in the private `Linkedin-autoposter` repository. There is no need to upload it twice.

These are public files; **never upload confidential or personally sensitive pictures**. A direct raw file URL is:

`https://raw.githubusercontent.com/contactoutsorz-alt/social-media-assets/main/jobsultan/shared-images/your-image.jpg`

Media must be accessible over HTTPS to Buffer without authentication. Test the URL and a real post before switching on image publishing; uploads alone do not trigger posts. The poster's media attachment and JobSultan Instagram automation are currently off pending setup.
