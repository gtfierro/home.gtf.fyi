---
title: "Making Your Academic Portfolio Website"
date: 2025-05-21T09:40:12-06:00
categories: ['Grad School','Student']
type: post
draft: true
---

Graduate students --- especially PhD students --- should have an up-to-date academic portfolio website outside of a Google Scholar or LinkedIn profile.
This post is a short guide to how to make a portfolio site and what to include on it.
I'll be linking to external documents and how-tos as much as possible to avoid having to repeat information that is best maintained by the original authors.

*This post is just a starting point. It contains the "breadcrumbs" to point you in the right direction for making a portfolio site. Send me an email if there is anything I should add or change!*

## What goes on an academic portfolio website?

Imagine you just came across an awesome paper, listened to a great conference talk, or got a recommendation to check out someone's work.
Where would you look for more information about that person? What kind of information are you looking for?

I usually Google the person's name to find out more about their research interests, recent publications, and possibly contact information for follow-up questions or future collaborations.
You should put together your own website to make this kind of information easy to find.
Here is a list of things to include on your website:
- A short bio (who you are, what you do, where you work)
- A list of your research interests
- Updated CV
- [ORCID](https://orcid.org/0000-0002-2081-4525) or other unique academic identifier
- Current affiliation and position
- [Google Scholar profile](https://scholar.google.com/citations?user=9wj4L7MAAAAJ&hl=en)
- Recent publications:
    - Title, PDF link, DOI, conference, acceptance rate, awards
    - **Bonus**: key figures, abstract for papers, links to code or data
- Professional social media profiles (if desired)
    - LinkedIn, GitHub, BlueSky, etc.
- (Optional) blog posts or other writing: this can be a great way to practice writing skills and also to disseminate ideas that are not ready for publication (or are difficult to publish).

My preference is to keep the website design itself simple, easy to navigate, and devoid of flashy animations or other non-essential features.
Most people visiting your academic portfolio are looking for specific information; anything that prevents or delays them from finding that information is a distraction.

My advice is to spend some time looking for the academic portfolio websites of senior and junior researchers in your field.
What elements of their websites do you like? Which elements made it difficult to find key information?

Look at my website below. Can you find all the information listed above? How did I do?

{{< figure width="50%" src="/img/portfolio-site.png" alt="Screenshot of my portfolio site">}}


## How to make an academic portfolio website

There are a few decisions to make when assembling your academic portfolio website.

1. **Do I buy a domain name?**. This is a personal choice; some hosting providers will give you a URL like `gtfierro.github.io`, but honestly I think having a domain name is worth the cost to establish a piece of online real estate that is tied to you. Domain names are easier to remember than long URLs, and it's generally a much better look! You can buy domain names for $10-20 per year from providers like [Squarespace](https://domains.squarespace.com) or [Namecheap](https://www.namecheap.com). More "unique" gTLDs (like `.io`) are generally more expensive, but it is always worth checking! Most of these domain name providers have an easy-to-use tool whereby you can check for available names. Some cool-sounding gTLDs to consider are `.me`, `.site`, `.dev`, `.tech`, and `.space`.
2. **Where do I host my website?**. It's 2025 and it is very cheap or free to host a website. Some options to consider are how much you time you want to spend on configuration and customization, and how much control you want over the way the website looks.
    - **Github Pages**: GitHub provides free hosting of your website if you host the source code of your website in a GitHub repository. If you don't mind the repository being public, you can do this using a free account! They maintain complete instructions for how to do this [here](https://pages.github.com). **I would recommend this option** as it offers flexibility in how to build your webiste. One caveat is that you can't adjust MIME-types for hosting static files or incorporate any server-side processing; if you need this, I recommend hosting your website on a VPS (virtual private server) or using a service like [Netlify](https://www.netlify.com/) or [Vercel](https://vercel.com/).
    - **University hosting**: usually your university will offer some sort of hosting service through their CRM (content resource management) system, like Wordpress {{< sn >}}At Mines, you can request a personal web page [here](https://brand.mines.edu/web-creation-and-editing-2/#personal){{< /sn >}}. This is a good option if you want your website on the university's domain, but keep in mind you are at the mercy of your IT department for changes/updates to the platform.
    - **VPS (virtual private server)**: if you are comfortable with Linux and want to have complete control over your website, you can rent a VPS from any large provider (like Google Cloud, Amazon Web Services, or Microsoft Azure) or smaller providers like [Digital Ocean](https://www.digitalocean.com/) or [Linode](https://www.linode.com/). This is a good option if you want to run a custom web application or need to host large files. These have the most flexibility but also requrie the most technical know-how and time to set up and maintain.
3. **What platform do I use to build my website?**
    - **Static site generators**: these are tools that take a set of files (usually Markdown) and generate your (static) website. They are great for academic portfolios because they are easy to use for common designs. Some popular options are [Hugo](https://gohugo.io/), [Jekyll](https://jekyllrb.com/), and [Pelican](https://blog.getpelican.com/). I personally use Hugo for my website and am generally happy with it. Most of these have lots of themes you can choose from, and if you know a little CSS you can adjust the theme to your liking. I would recommend using a static site generator if you are comfortable with code and want to have a lot of control over the design of your website.
    - **WYSIWYG (What You See Is What You Get)**: if you are not comfortable with code, there are a number of website builders that allow you to drag-and-drop elements to build your website. Some popular options are [Wordpress](https://wordpress.org), [Wix](https://www.wix.com/), [Squarespace](https://www.squarespace.com/), and [Weebly](https://www.weebly.com/). These are easy to use but can be expensive and have limited customization options. I can't comment on how well they work for academic portfolios, and I think they are generally not worth the cost for something as simple as a static website.

## Maintaining Your Website

It is very important to keep your website up-to-date.
I update my website every time I publish a new paper, give a talk, or have a piece of news to share.
Over time, the website will become an excellent record of everything you have accomplished.

Abandoned websites are sad. Out-of-date websites make it difficult to find information. I have had past opportunities for collaboration stymied by a lack of an up-to-date email address.
You should set up your website in a way that makes it easy to update. It only takes me 30 seconds to add a new publication to my website, and I do it every time I publish a new paper.

## Just Do It!

The best way to learn how to put together an academic portfolio website is to just do it!
You'll learn about web design, domain names, configuring web platforms, and how to advertise your work and present yourself as a professional researcher.

Send me an email if you have any suggestions for other links or tutorials to include here, or if any information is wrong or out-of-date.

Good luck!
