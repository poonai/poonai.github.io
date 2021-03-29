---
title: "Can differential privacy protects our privacy?"
date: 2021-03-29T14:27:16+05:30
draft: false
---

I'm a mediocre engineer who does systems work and never had experience in the typical user-facing software space. I've contributed to software that scales but never really had a chance to experience the vibe of serving millions of users.

Recently, one of my friends explained to me the kind of events they track in their startup. I felt sick after hearing about the kind of events that they track, which are typically very personal to the user. Companies collect data ranging from the user's geolocation to the user-installed app names(maybe to hike the price if the competitor's app is not present on the user phone). 

I decided to dig deeper and see whether any privacy-friendly tracking solution exists and, that took me to [Apple\'s paper](https://docs-assets.developer.apple.com/ml-research/papers/learning-with-privacy-at-scale.pdf). This paper explains how Apple leveraged count-min-sketch with some noise to deduce the inference of user behaviour, without hindering user privacy.

Usually, researchers have their own real-world assumptions which may not be applicable everywhere. I ran a small [experiment](https://github.com/poonai/diffrential_privacy/blob/master/cms_test.go#L30) to estimate the popular view on a project management app to validate the paper.
```go
    // we are tracking what view users are using in their project management app.
    // 6k users are using list view.
    track(6000, "list")
    // 9k user using board view.
    track(9000, "board")
    // 2k user using calendar view.
    track(2000, "calendar")
```
The variance between the actual inference and the inference calculated via differential privacy is not that large. 
```go
    fmt.Println("estimate for list", server.Estimate([]byte("list")))
    fmt.Println("estimate for board", server.Estimate([]byte("board")))
    fmt.Println("estimate for calendar", server.Estimate([]byte("calendar")))
    // output
    // estimate for list 6572.1029024055715
    // estimate for board 9154.186791339975
    // estimate for calendar 1157.801902649071
```
  
I presented it to my friend and asked him whether his company would consider using such tech.

Unfortunately, the inference of users' behaviour alone is not enough, they would also want to send notifications based on certain events.

For example, if the user dropped off on a certain app screen without performing an action, the tracking system should be able to send a notification, which nudges the user to complete the action. Apparently, the tracking service tracks events at the [user level](https://docs.moengage.com/docs/tracking-user-attributes#default-user-attributes). 

Companies don't just want analytics, they also want to target the user. which reminds me of the quote from the movie `The Social Dilemma` 
>We want to psychologically figure out how to manipulate you as fast as possible
 
### Closing Thoughts:
Differential Privacy looks good on paper but differential privacy alone is not enough to cater to big companies' needs. There are some use cases, where I think differential privacy can be deployed.
- customers' sensitive data can be tracked.
- privacy-focused applications.

I would love to hear where else differential-privacy can be plugged in. [My profile](https://twitter.com/poonai_) if anyone wants to reach out.

