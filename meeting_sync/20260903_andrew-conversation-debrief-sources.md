# Sources — Conversation with Andrew, 2026-09-03

> ⚠️ Uncorrected originals below (Granola notes + raw transcript). The Granola notes are unverified reference; the cleaned, annotated version lives in [20260903_andrew-conversation-debrief.md](20260903_andrew-conversation-debrief.md).

## Granola Notes
# Losslessness: Statistical vs. Task-Level

- Formal losslessness means sampling probabilities are identical to the target model across the full vocabulary
  - Original speculative decoding papers provided a mathematical basis for this claim
  - Whether even the original papers verified this empirically at the token level is unclear
- In practice, companies claim losslessness by passing benchmark tasks (math, coding, GSM8K) while gaining speed
  - This is not sufficient evidence of statistical losslessness
  - D-Flash and similar models assert losslessness but provide no quantitative distributional evidence
- The real industry goal has shifted: Pareto frontier of inference speed vs. quality preservation, not strict statistical guarantees

# Quality Degradation and Benchmark Overfitting

- 83% of real-world task domains are not covered by the benchmarks used to validate speculative decoding models
  - Observed degradation on frontend design, creative writing, and other non-verifiable tasks
  - Figure 11 demo shows D-Flash completing a task faster but producing broken output that nobody checks
- Analogy: 1992 NHTSA crash test expansion, where cars that scored well on the old test failed the new one
  - Companies may be hill-climbing on a narrow test set, overfitting speculative decoding to math/coding
- Open question: whether quality collapse stems from the speculative decoding algorithm itself, or from the underlying base model already being overtrained on verifiable tasks via RL post-training
- Open question: distillation from a large, RL-overtrained model to a smaller draft model may amplify the math/coding bias and worsen generalization on other domains
- Open question: whether the original losslessness proof holds in practice, given that it relies on correct rejection sampling and residual mass computation

# Evidence, Framing, and Next Steps

- Token-level computation planned: extract logits over full vocabulary, compute distributional divergence (e.g. Bregman divergence) between draft and target model
  - This would provide concrete, quantitative evidence beyond benchmark pass rates
- Two levels of lossiness to distinguish:
  1. Algorithmic: even “lossless” configurations may deviate at the token level
  2. Overfitting: draft models degrade on tasks outside the training distribution
- Broader task evaluation already underway (frontend design, creative writing) to show degradation outside standard benchmarks
- DeepSeek/DeepSpec training recipe and data distribution (Open-Platypus dataset) to be reviewed; data skewed toward math, coding, chat
- Article scope: currently wide-ranging (literature review, empirical findings, tutorial, forward-looking); may need trimming or tighter focus depending on venue expectations
  - Plan to email the venue to clarify what they are looking for before revising scope

# Next Steps

- **Run token-level logit distribution comparisons between draft and target models**
- **Review DeepSeek/DeepSpec training recipe and Open-Platypus data distribution**
- **Email the venue to clarify article scope and format expectations**

---

Chat with meeting transcript: https://notes.granola.ai/t/12e1ecc3-af34-4b07-acdf-7f4d7032adf2

## Slack Notes
Lily Zhang  [11:26 AM]
Hi Andrew, https://neurips2026-speculative-decoding.vercel.app/
[11:28 AM]I am submitting to the neurips education track, will you be willing to look it today before the deadline, Fridat 09.04? i feel you will be a great reviewer.
[11:28 AM]https://neurips.cc/Conferences/2026/CallforEducationalResources
Andrew Hartnett  [11:30 AM]
Yes!
[11:30 AM]It will be a bit late tonight, though if that’s OK
Lily Zhang  [11:45 AM]
tonight is totally fine
[11:45 AM]I want to get your advice on the soul of this educational material.
[11:46 AM]The NeurIPS submission requires teaching on the concept of AI research from the past few years, including papers from NeurIPS 2026 or other conferences. That's why the current writing is centered around some established work.
[11:46 AM]But they also include novel work such as LosslessBench. So I'm debating what should be a good title for this educational piece.
Andrew Hartnett  [11:51 AM]
I would love to be a reviewer for this (more broadly)
Lily Zhang  [11:52 AM]
sounds good, take your time. I also have two title candidates, appreciate your feedbacks!


Speculative Decoding: What Lossless Means, What It Doesn't, and How to Test It
LosslessBench: Defining and Testing Loss in Speculative Decoding
Andrew Hartnett  [1:37 PM]
I'm sure you are working on this frantically ... so some early feedback (I'll get to the rest tonight)
[1:38 PM]1) I like your current title more than your second one .... I think its important in a pedagogical article to hit the reader with the anchor/term that they will recognize ... here that is "Speculative Decoding"
[1:40 PM]2) You need to expand your first paragraph or your audience will be too small. You need to take a few sentences and explain what speculative decoding is ... you need to start with why we need it (speeding up inference) and how it works (fast draft model + verification).  As it is now .. you are too deep, too fast. You will lose anyone that doesn't know what "draft" is in this context.
[1:40 PM]3) Is figure 1 going to be animated??
[1:41 PM]4) Your first paragraph in "What lossless means" is too jargon heavy ... B200, SGLang, "vanilla" in this context all require a lot of insider knowledge ..  at the very least you might want to have a hover over glossery?
[1:42 PM]... okay ... gotta go coach a soccer practice for little kids ... be back later
Lily Zhang  [4:22 PM]
thanks, this is very helpful!
[4:22 PM]https://neurips2026-speculative-decoding.vercel.app/
[4:23 PM]The first paragraph explains what speculative decoding is, why it is faster than vanilla Model decoding, and who is using it. This is my hope to attract an audience.

Do you think anything can be improved here?
Screenshot 2026-09-03 at 4.23.12 PM.png Andrew Hartnett  [4:46 PM]
Yeah ... I think you need to back up ... you jump too far ahead ...if you start with "speculative decoding decouples draft generation from target verification" you will loose a huge audience ... basically everyone who has heard the term but doesn't really know where it fits in the modern AI world or how it works
[4:50 PM]You need to start with the idea that:

autoregressive decoding (at inference time) is a major bottleneck (up to you whether you want to get into the "why")
speculative decoding was introduced in 2023 as an approach to accelerate inference
it works by leveraging a lighweight model to generate "drafts" or short subsequences (a smaller model can do this more quickly) -- then using the full model to verify these drafts
importantly ... this procedure is *lossless*, but we'll get to what that means and why it is important (you want to set the hook)
if well aligned, this can speed up inference significantly -- because the draft + verifier combo is able to generate and accept sequence chunks rather than one token at a time.
(edited)
Andrew Hartnett  [5:07 PM]
In table 1 ... you want to introduce your metrics in a sensible order ... for example ... you should introduce acceptance length (and \tau) before per-token latency (since you use \tau) (edited) 
[5:08 PM]in your example ... I'd be in favor of using a non-integer /tau as that seems unlikely ??
[5:10 PM]But how is it lossless in theory? ... I think you need to cover what it means to be lossless in this context ... for many readers lossless has connotations with image/video compression and its not immediately clear what it means in this context
[5:11 PM]I think you need to emphasize that this only works because ... upon rejection you sample from the residual ...
Lily: This is a very good point. I didn't realize that starting sentence isn't appealing for many people. https://latitude-ai-llc.slack.com/archives/D07DGEZQPCP/p1788479190614199
Getting kids to bed and then I'll keep going
Lily Zhang  [5:19 PM]
Thank you very much. I'm hoping to collect your thoughts on Section 3, What's next?
[5:20 PM]There are other surveys or blogs writing about speculative decoding. And I want to differentiate this writing piece from others, which maybe made me jump too fast.
Lily Zhang  [5:22 PM]
How would we balance between having enough context versus covering more intermediate content? Can we say the introduction + Section 1 covers more beginner conten, If you are already aware of it, feel free to skip to Sections 2 and 3. In this way, we would provide options. What do you think?
Andrew Hartnett  [6:40 PM]
let me read the entire thing before I give advice here
Andrew Hartnett  [7:16 PM]
More notes on section 1:
15 repliesAndrew Hartnett  [7:17 PM]
before I get to 1.1 I should know why its important that this is lossless --- this is important for the discussion we want to have in section 2 ... reading this far I do not yet have any intuition for why this is important ... or what would happen if it were lossy
[7:17 PM]section 1.1 (Eagle) ...
I think you need to explicitly say that the target model is the big LLM (the one we are trying to accelerate, the one used in verification)[7:17 PM]how is a decoder layer different from an "extra prediciton head" .. those could be synonomous
[7:18 PM]figure 2 ... you are using vanilla for the second time in the article ... and this time it refers to something else (previously it referred to no speculative decoding ... here it refers to the original paper's algorithm) ... I think you need to refer to the OG speculative encoding scheme in a different way
[7:18 PM]This should help me build intuition and a sense of scale ... for example: How big is a draft model/head? I don't have a good sense yet? And what is the intuition here? A speed up of 6x ... should my intuition be that means that the acceptance length is > 6 tokens? (likely ~7 or 8 given the draft time??)
[7:18 PM]The EAGLE section is titled as "longer acceptance length" ... but the numbers provided are only speedups ... can we really attribute that to longer acceptance length? Can we show the reader that?
[7:19 PM]DFlash section .... numbers don't add up here .. Eagle-3 is up to 6.5x faster ... DFlash is 6x faster ... but also 2.5x faster than eagle-3??
[7:19 PM]DSpark section ... it is not clear in the text that DSpark this is an extension of the block diffusion approach of DFlash .... so statements like A lightweight sequential head restores dependencies inside the block, so later positions can condition on earlier ones. don't immediately click. You need to get to figure 4 to put it together.
[7:20 PM]Dspark section --- we need some intuition injection here ... DSpark improves accepted length by 16–31% over state-of-the-art drafters  --- this has to mean that the "default" block size for DSpark is greater than the optimal tuning for DFlash (since DFlash doesn't have the ability to drop the tail when it should)??  Why does this help this much .. the intuition thus far is that verifying 1 vs 5 vs 10 tokens is about the same cost?  What does that cost curve actually look like?  It is interesting that you say it "cuts verfication time" but the compelling metric is that it extends the accepted length ... we definitely need some intuition about how those are connected.
[7:21 PM]It accelerates per-user generation by 60–85% at matched throughput over the MTP-1 production baseline --- this is too jargony
[7:21 PM]DFlash2 section ... again I'm wanting a little more intuition here ... is this doing beam search? kind of? Coherent path through a tree? or a set of trees?
[7:22 PM]DFlash2 section -- Metrics match the claim here showing that we extend output per verification pass!! (this is good).  The 2.7-3.4x number is still at odds with the 6x in the DFlash section ... though I like the number here better because it is more specific (pinned to a specific model)
[7:22 PM]your `~Note that DFlash 2~ ` section is backwards I think ... i.e. should stay sequential ... not parallel.
[7:22 PM]Table 2 --- the speed up numbers don't make sense (with their respective \tau) ... I would drop them
[7:23 PM]You end section 1 with: So far we have covered what lossless means. In the next section, we will discuss what lossless does not mean. ... but we haven't really spent anytime on that ... or at least not why its important ... or what would happen if speculative decoder were lossy
Please understand that I am dumping notes ... and they all sound like critiques ... because I assume that is what is helpful right now. I am enjoying reading this and a lot of it is wonderful ... I'm just nit picking right now
Andrew Hartnett  [7:24 PM]
Notes on section 2:
18 repliesAndrew Hartnett  [7:26 PM]
Even in the original papers, lossless is not unconditional. --- it feels like you should go on to explain what the conditions are in the original papers
[7:26 PM]what is the relaxed acceptance variant?
[7:28 PM]Can you provide some intuition about why this is temperature dependent? The math in the text box that starts with P(x is emitted) in section one make this seem like an identity ... there is no temperature in that math

You end up doing both of these things ^^ ... but the ordering feels off. Temperature is only a problem because you've strayed away from pure rejection sampling (edited) 
[7:29 PM]At temperature 1, decoding is random ... shouldn't this be temperature == infinity?
[7:31 PM]I think you need to say ... very clearly and directly ... that in attempt to get greater speedups ... some of these methods have strayed from canonical rejection sampling ... and that introduces a bias
Andrew Hartnett  [7:38 PM]
Lastly, the production stack is complicated: it accelerates inference well beyond speculative decoding. Weights are quantized (lossy). KV caches are compressed (lossy). The serving system adds KV-cache-aware routing and prefill-decode disaggregation on top.

This is very jargon-y again. Its fine to leave ... but need to budget stuff like this judiciously. I think it won't be understood/absorbed by most of the readers
[7:40 PM]Outside them, the empirical evidence for losslessness is simply absent. -- I think you need to explain to the reader how losslessness is measured within the core domains ... i.e. what is the metric for losslessness? How is it measured?  I assume you generate a bunch of text both with and w/o your speculative decoding algorithm ... and compare the distributions. (Maybe you keep the logits themselves and not the sampled ouputs)?/
Andrew Hartnett  [7:46 PM]
I don't fully understand Lossless Bench? It seems like an awesome judge of quality degradation --- and that is useful ... but I guess I assume that a losslessness metric should be a measure in distribution space ... like TV or KL (or some other bregman divergence)?? This feels more like a general quality vs. speed tradeoff evaluation
Lily Zhang  [7:47 PM]
LosslessBench is a benchmark I have created, covering domains beyond coding and math.
[7:47 PM]https://neurips2026-speculative-decoding.vercel.app/#losslessbench
Andrew Hartnett  [7:47 PM]
Yeah .. and its awesome ... but it doesn't feel like it measures loss
Lily Zhang  [7:47 PM]
See Figure 11 here
Andrew Hartnett  [7:48 PM]
I see it ... and again its great ... but loss (losslessness) here is a statistical distribution concept ...
Lily Zhang  [7:49 PM]
speculative decoding models like DFlash or DSpark all claim to be lossless on any task, but that is only true on some very simple coding tasks. That's why I want to create lossless benchmarks to show that when you evaluate beyond coding and math, there actually is inference quality degradation.
Andrew Hartnett  [7:49 PM]
and so I would expect a measure of that property to be like the KL divergence (or similar) between some gob of output tokens ... or of logits
[7:50 PM]how does this show they are lossy? you need some idea of what the variance or distribution is from the vanilla model?
[7:50 PM]do you have a sec to talk .. might be easier?
Lily Zhang  [7:50 PM]
sure
Lily Zhang  [8:09 PM]
https://arxiv.org/pdf/2602.06036 dflash has no direct evidence on being lossless
Lily Zhang  [8:17 PM]
https://neurips2026-speculative-decoding.vercel.app/#losslessbench
[8:18 PM]https://huggingface.co/datasets/mlabonne/open-perfectblend training data from deepspec
huggingface.comlabonne/open-perfectblend · Datasets at Hugging FaceWe’re on a journey to advance and democratize artificial intelligence through open source and open science.huggingface.co[8:19 PM]https://github.com/deepseek-ai/DeepSpec
GitHubGitHub - deepseek-ai/DeepSpec: DeepSpec: a full-stack codebase for training and evaluating speculative decoding algorithmsDeepSpec: a full-stack codebase for training and evaluating speculative decoding algorithms - deepseek-ai/DeepSpecGitHubAndrew Hartnett  [8:30 PM]
Notes on section 3
Andrew Hartnett  [8:31 PM]
The multimodal stuff makes a lot of sense -- its a nice well written section (sidenote is I think it might be some slight evidence towards my "small models don't generalize as well" theory)

does the token density matter here? My understanding is that vision tokens carry a lot more information than text tokens ... as a result there just might not be as much juice to squeeze.  I.e. its just a much harder problem to correctly predict a series of vision tokens. (edited) 
[8:33 PM]The tool call stuff seems very reminiscent of CPU speculative execution (and branch prediction) .... which is really the origin of speculative decoding being called "speculative" decoding

while the desired outcome is the same ... the approach needs to be very different ... much more like a CPU. We aren't just taking advantage of the parallelism of validation anymore (edited) 
[8:37 PM]3.3 doesn't seem to fit within the larger article ... I understand the trend here .... first it was quantization ... now its speculative decoding, but I think this section does more harm than good (the last thing the reader reads is the most tangential).  I might replace it with a more holistic conclusion?
Lily Zhang  [9:08 PM]
I agree with 3.3 doesn't seem to fit within the larger article , it is a bit odd, i can delete it
[9:08 PM]would you suggest just end with multimodal, drop the spec tool section too? @ahartnett

## Raw Transcript

Meeting Title: Speculative decoding — lossless claims, quality degradation, and benchmark overfitting with Andrew
Date: Sep 3
Meeting participants: Lily Zhang

Transcript:
Me: Okay. Hi, Andrew. Can you hear me? Okay. You want me to join the I can also join the Zoom. Hey, Andrew. Ongoing well. Thank you so much for putting so much
Them: Hey. How's it going? No worries. I I I I wanna make sure
Me: Thoughts. I really appreciate it.
Them: That I, like, know, caveat this so that I'm enjoying it very much. And I'm just providing criticism because I feel like that's you know, what you need when you have twenty four hours to make something better, not
Me: Yeah.
Them: Not because I think it's it's it's bad.
Me: No. No. No. The the main teacher comments are the best. So, yeah, let's talk about the lost less bench idea. Right?
Them: Yeah.
Me: I I think I know what you are going for. And because loss if we read the article, I think it maybe leave the impression of you know, measuring something like a KL divergence or log probability of the token, So when people read about lossless bench, they would expect something like that. I think I I had also considered that. Like, we host the model and get the token probability, calculate the draft distribution and also the the target model distribution. But that wouldn't work because the target model will only accept the draft token when it's aligned with the probability it can accept. So if we do that, it wouldn't show anything.
Them: So like, I mean but but I I think that's what I'm that's what lossless means here.
Me: Hmm、そう、 I was hoping to define loss as both a speed, the inference speed, which means that there shouldn't be when you have, like, inference acceleration, we're expecting both the speed to be improved and also the the quality to be maintained. Right? So when I try to convey here is more like even though the speed improved, but we shouldn't expect any quality degradation. If we want to show quality degradation, we could show either from the the token level or we can show it on a task.
Them: Right. But but
Me: Yeah.
Them: Right. So, like, I mean, that's an argument you need to make. Right? That, like, that, you know, okay. You know, when we talk about being lossless, what what that that's really sort of a and a statement about the sampling probabilities for you know, every token in the vocabulary.
Me: Mhmm.
Them: As being identical to those from you know, from the core distribution. Right? And and so you know, I think you I think I think you you kinda need to say that and then you can say something along the lines of, like, well, you know, we can measure that. But but that really has you know, like like, that might not be the most useful thing for someone who's you know, building you know, speculative decoding algorithms or, you know, ML in general, care you know, one of the things that's that's sort of evidenced by you know, all of these algorithm developments is what we're actually is this sort of Pareto frontier of like, inference acceleration with preservation of quality. And we don't care as much about the statistical guarantee as we care about, like, the utility and perceptual like, perceptual evaluation. Right?
Me: Mhmm. Yeah.
Them: And I think and I think you can make an argument that that, like, this is obviously what companies are doing, right, because of the just the, like, the sheer economics of speeding up inference by five x, Right? And maybe they're over indexing on a couple small domains. They really need to be looking at a wider set and this provides this. But, like, I you know, I guess one of my one of my one of the questions, you know, that I would have here is, like, let's take a look at, you figure 11 in your thing here. Right? If you asked the vanilla model, to do this task 10 times, does it ever produce something like the flash?
Me: Oh,
Them: Like, does it ever mess up?
Me: So
Them: You know?
Me: Yeah.
Them: Is
Me: Mhmm.
Them: Like like, is the flash, you know, are we just seeing one outcome that actually is from the distribution of the vanilla model? Or has the bias that we've been introduced you know, really degraded the quality of the model?
Me: So number one, I I feel like you you have brought up, like, a several points. The first one is is a task we designed here answer what people build security pooling for. So sofort so, like, if you look at the the table three, right? Which is eagle three d flash, d spark, and deep spec, They test on very simple such as GS eight k, mass, this one. Right? And on this benchmark, they would usually measure the speed up. The tau acceptance lens, and also, like, pass rate how well they perform on this task. So these are all, like, the dataset they are evaluating. Right?
Them: Right. But but they don't do they use that to make a claim of being lossless? Because, like, that's
Me: Yeah,
Them: That's not sufficient to make a claim of being lossless.
Me: The user the user to make a claim that they can pass all this benchmark. While gaining speed up by, like, 2%, 3%.
Them: Okay. We've looked
Me: That's Mhmm.
Them: But but, like I mean, I I don't know. Like, I guess if I think about the speculative decoding story, right, like, it's you know, it starts with these two original papers. Right? And the original papers are are kind of saying, like, hey. There is a free lunch here. We can speed things up, and, like, without any change to the statistics of our model. Which is, like, really cool. Right? It's a free lunch. Right? And then what everybody did is like, oh, that's great, except I'm not really interested in a 1.3 x speed up. I want a six x speed up. Right? So you know, they broke you know, they would say relaxed. Right? But they, like, broke the preconditions that made this a free lunch. Right? And now it's not a free lunch. It's like now you are you it is lossy. But I guess my point is that, like, you know, I guess I'm I'm surprised that anybody is using these, like, pass rate on a benchmark to say they're lossless. I can see them sort of saying that, like, using the pass rate to say, hey. We're lossy, but it doesn't matter for the things you care about. Maybe you wanna say, you know, maybe you wanna say, like, pump the brakes there. You know? That you're like, that claim that that these companies are making isn't a good claim because 83% of what people are doing doesn't fall into these So, like, you're not speaking for me when you say there's nothing you know, that degrades on what I care about. But yeah. I know.
Me: Yeah. So I think they are even the very first few paper they evaluated against is a simple benchmark. They claim they are lossless because they can still pass this benchmark. And, with speed up, And I I think they're because they are conditioned on the the mathematical you know the the equation rate for係 The equation under 係 like, section like, the one above
Them: Sure.
Me: Like, here. Right? Maybe I can share my screen.
Them: Yep.
Me: Here, can you see the screen?
Them: Yeah.
Me: So this equation effective data proves it it is lossless. Right? Because you can achieve the final the probability to be equivalent to the target probability.
Them: Right. But that's
Me: Mhmm.
Them: But that's only true if you, like, if you're doing, like, this this rely like, that first line, right, relies on you essentially doing rejection sampling and the and it also relies on you sort of correctly computing the residual mass.
Me: Yeah.
Them: And I think your your point is that like, your like, so your point is that you know, if you kinda scroll down, to figure seven, Right? Like, in an effort to speed these things up, they're relaxing stuff like this. Right? And and so, like, you know, this this right here, when I think of lossless, right, Like, this is what I like, this is what I imagine. Right? Like, middle panel represents a form of lossless speculative decoding.
Me: I see. Yeah.
Them: And the right panel is lossy.
Me: Mhmm.
Them: You know? And it's like a lot like, companies are rolling out algorithms that are, like, the right bar that are lossy, but they can argue that, like, hey. I know this is but, it still works for all the things you care about. And and and your point is that, like, well, no. It doesn't. It works for the small benchmarks that you say we care about, which doesn't really represent, you know, the full distribution of of
Me: Mhmm. Yeah.
Them: Tasks. But, like but, like, this is like, this this graph is what I, you know, is the sort of statistical side.
Me: Yeah.
Them: You know, like like, I guess maybe I'd maybe I I different way of saying this, right, is if if what I you know, if what I evaluate is whether or not the model still thinks the best pet is a dog. Then, like, oh, all the model looks great. Because it tells me the best pet is a dog. You know? Just as often as the the full model.
Me: Yeah.
Them: But but that doesn't mean that the distribution is the same.
Me: Mhmm. Yeah.
Them: Right? I I I'm not measuring whether it thinks the best the best pet is a cat. And that's sort of the equivalent to, like, your like, your front end development bench is, like, the equivalent of ask of this asking, like, evaluating is the best pet a cat. Right?
Me: So this one, right, I thought about it to be included in the lossless bench as well. We can check we can relax the threshold to see show people how lossy it is. But there's another counterargument. So the when the inference provider or anyone deploy the model, there is a way for you to configure the model to run faster. Right? But that's up to you. Up to the inference provider. It's a matter of a configuration. So it's a very subjective way to make a lossy inference. What I wanted to show here in the lossless bench was even today, like, d flash claimed to be lossless across everything. Right? For example, it was tested on this much benchmark. But I think people don't realize that 83% of the domain tasks are not being tested by all of these inference acceleration algorithms. So they choose a easy route And a lot of us, we use those task. Right? So I want to show even like, maybe it's more like a like, I want to show that even for, for the model itself, they are serving has, like, lots of degradation on the front end design. Creative writing. This is a very objective for me to show there's the issue here. I could also show the the the relaxed configuration. But I I feel like that's a hard argument because people, like, say, oh, you cannot argue d fly. She's lost lossy because you relaxed the rule by yourself. Because that's known. You are just you know, showing that do you see what I mean here? It's it's not like a it's a, like, harder argument to make.
Them: Yeah. I mean, I guess the, like I'm, like, looking through
Me: Mhmm.
Them: I'm looking like, I think the hard thing. Right? And and maybe this is maybe I'm being a little bit of a kind of a a hard ass here, but I'm looking through the d flash paper and I don't see anything in the defect DFLASH paper that that I see as evidence that they are lossless.
Me: Oh, det det det tartar vara.
Them: Right. I'm I'm saying I'm I'm saying they they say the word, but I don't see any quantitative substance
Me: Yeah, yeah.
Them: To to indicate, like, I don't see any quantitative evidence that they are lossless.
Me: They don't have any evidence because they built a pump the belief here. The equation we just show,
Them: Right. But that, like,
Me: So the lossless. Yeah.
Them: Yeah. But, I mean, but but but it but they're like, that's not yeah. I yeah, I don't believe I don't believe it's lossless.
Me: Okay.
Them: But,
Me: Okay. So you don't believe there's losslets How do you want to convey that to the audience?
Them: Yeah. I mean, I think, like, I think you I think you need a giant I think you need to extract the the like, the logit
Me: Mhmm.
Them: For the whole vocabulary over a wide range of tasks. And I think you need to compute whether it's the you know, some sort of Bergman divergence or some sort of distributional metric measure that says they're not the same. But
Me: That's more fundamental. If I do that, I think I can maybe
Them: I mean, I think
Me: That that's not Yep.
Them: So so I I guess, like, you know and and maybe maybe I'm being unfair here. Because, like, because, you know, looking through this d flash paper, I can see you're sort of responding in kind. But, like, I think you're making a I think the story that or, like, the thing that you know, the story arc that I see is, like, okay, speculative decoding came out. There's, like, a theoretical reason to think it's sort of lossless. But we've but it's, you know, it's it's entered the realm of sort of, like, like like, companies are making all these improvements because there's real economic
Me: Example
Them: Value in doing so. And they're sort of assuming de facto that the original theoretical justification holds And not really providing you know, empirical verify verification of that. And the sort of the limited signal that they do provide is that is is really just a measure of the model performance on a subset of tasks with speculative coding is still good.
Me: Yeah. Exactly. Yep.
Them: Like, However, if you look outside of that set of tasks,
Me: Mhmm.
Them: You know, there really is quality degradation.
Me: Mhmm. Yeah.
Them: Like, here's an email. Here's an example of, like, you know, like, one of the things I think of, right, is that I forget what year it was. It's like 1992 or something. That the that NHTSA changed the like, crash test the set of crash tests that had to be done for a new car. And if you look in, like, 1991, almost every car company had an a. Then if you look in, like, 1992, like, only only, like, two companies passed the new tests. Like, because, basically, they had overfit to the specificities of, like, a like, a very, you know, constructive set of tasks. And I think, like, what we're arguing here is that, like, you know, you're you're basically arguing that as companies sort of hill climb on speculative decoding algorithms They are overfitting to a really limited test set.
Me: Ja.
Them: And what it's gonna leave us with is is models that are really performative, I you know, that are both fast and performative at, you know, at at, like, coding and math but suffer real degradations when it comes to other tasks.
Me: Exactly.
Them: And so, like, what is what does that mean for you? It's like, well, it means that if you are out of one of those tasks and you have knobs
Me: Yeah. Mhmm.
Them: You can control in your inference provider you really need to kinda back off aggressive speculative decoding. Because you're you're paying for it even though you know, DeepSeek isn't advertising that to you.
Me: Mhmm. But I think the argument is very good. But there are, like, two level of lossy. One level of loss is from the algorithm itself. Even though it claimed to be lossless. Right? When we output, I will also try to do the log probability con computation. Between the draft and target. Then we wanna know concretely what's the difference and the gap. Number one, Number two, like, the overfitting issue. They are now overfitting too much and the coding. The neural models, these sucks at front end design, any creative task, creative writing. So it's already we're eating the outcome. So I want to review that to people. Number three, instead you you can tune the knobs. Right? You could tune the knobs to be, like, temperature zero and then respect to the acceptance you are still using when you are using a specular decoding model, there are not much room you can play with if itself is already lossy and overfitting the coding and mass. Mass, So what you really want to do is that we want to bring awareness for people when you train a
Them: Muy
Me: Faster model, you want to be more all rounded and balanced instead of taking a shortcut.
Them: Well so so, I mean, I I think the thing you so sorry. I think I think a couple so one thing here is I am operating under the premise. That the original speculative decoding paper or the original two papers were in fact lossless. And I guess I don't know if that's entirely true, but I assume they are.
Me: Am no I'm not sure either. They also didn't they have done, like, a mathematical proving, but I don't know if they have done, like, a comprehensive, like, token
Them: The second
Me: Computation there.
Them: The second the second piece here is that, you know, I think one one of the things that we're trying to separate is you know, the models in general like, the models themselves are overfitting to coding and science and math. Tasks. Right? I I think you wanna make the argument that speculative decoding is also is is making that worse or is also overfitting to those tasks.
Me: So right now, when they train the model, they only pick up the task that's easy to verify, which is coding and a mass. They don't do anything on other end. That's why the model doesn't do very well.
Them: I mean I mean, mean because this is how, like, RL post training works. Right?
Me: Yeah.
Them: But, like, I guess, how is I I guess it's not you know, maybe this is something that I'm missing. It's like, how is a speculative decoding model trained? Is it trained in the same way? Does it also go through kind of RL post training?
Me: They don't do RL pose training but they are doing some type similar to SFT. They take another smaller model from the same domain. For example, when you have a big quint model, right,
Them: Yeah?
Me: Let's say, like, 100, like, one t b, very big, then they will pick up a smaller one. Let's say, like, with a to b. And then trying to trend our model to imitate the token distribution like target model. It's nothing related with RL. It's more like close to SFT. And they use maybe, like like, coding and mass. As a way to validate the the token distribution are very similar across a small draft model and a target model.
Them: But why? See, that that part doesn't make sense to me. Because it feels like if you're just trying to do it it feels to me that if you're just trying to train a small model, match the target match a target distribution, that, like, you shouldn't care what the domain is. You should just generate whatever you want.
Me: But without measuring, how do you know? Right? So for example, if you go to figure 11 in the website, figure 11, if you click replay,
Them: Yep.
Me: Can also show that.
Them: Yeah. Yeah. I know. I've done it a couple times.
Me: Yeah. So if you click replay for figure 11, right, essentially, what it does is it show you how those token get generated in real time through vanilla, eagle three, and g flash. I also render that. So d flash would always post saying, oh, we are lossless, and we are so fast We're the fastest. We finish the task in 3.1 task. But look at the generated doesn't even work.
Them: Great.
Me: But nobody nobody checked these
Them: Right.
Me: Calendar's ineffective. People look at the speed numbers.
Them: Red. And and this seems well worth checking, but I guess I guess my my point is I don't have a good intuition for
Me: Mhmm.
Them: Like, like, the the training process. Like, I guess my point is that, you know, I feel like at this point, we all you know, we don't know every company's secret sauce, but we all kind of more or less understand how the core how the base model is trained.
Me: So
Them: We understand
Me: Yeah.
Them: The unsupervised pretraining followed by SFT, followed by you know, like, RL. Like, we we understand the basic ingredients. You know? Like, all of these speculative decoding models. Right? Have a have a have a have their own generative model. Right? Whether it's a small diffusion model or us another LLM or whatever it might be. Right? They have their they have their own model in there. Right? And I guess I don't know what the training recipe for that model typically looks like.
Me: So we have a training recipe. For example, DeepSeq open source their training recipe called deep stack. I will also include a tutorial how to trend those models. In the tutorial. I'm also studying that right now. So and I shared with you the repo the deep SPAC training, and the evaluation framework. And they actually open source all the weights they have trained. They also share the dataset they are using. Which is called open perfect plan. You can see the data distribution there, which is again mass chatting and coding.
Them: Okay. But, like but but so, you know, the interesting thing is if I look at if I did like, this is so you know, sort of what I how do I pick which screen I oh, I can't share my screen. If if I go to that page, right, and I look at under workflow, if I run under train if I look under training right at the top, it says train a draft model against cached target outputs. Right? That's sort of what I would assume. Right? I can sort of generate infinite training data for my my my draft model because I'm just trying to estimate whatever the, like, the probability distribution generated by the target model. And so, like, so, like, one of a couple things is going on. One is, like, I'm making a bunch of you know, like, either either what's happening is having a smaller model to begin with. Is sort of amplifying some bias in the underlying base model. And the base model is certainly been overtrained like, over focused on math and coding and things like this because it's largely trained through RL. Right? And that's only working sort of verifiable domains. So, like, maybe, you know, what happens is you overtrain the base model on these verifiable tasks. And then, you know, what's happening here is it looks like pretty vanilla distillation. And if I distill if I try to do vanilla distillation in this, you know, on these overly trained models, maybe the the kind of, like, you you know, like, one of the magic of going to a bigger model is that generalization improves. Right? So imagine I take this big model, and then I I I, like, train the crap out of it on math and coding. And then I distill to a smaller model and I kind of fall under that real generalization threshold. But I'm now distilling, like, like, I could I could see a world where that makes the the the, like, performance gap between math and and coding and other things even worse. You know, another thing is that there's there's actually something you know, super biased or broken in the in the way that that the the speculative decoding algorithm actually runs. Right? And you have an example of that with, like, you know, the verification scheduling in DeepSeq where they, like, are peeking into the future and and breaking some underlying, you know, assumptions. But but but, I mean, I you know, to me the to me, the story feels like speculative decoding is supposed to be a free lunch. Practice, it's really not.
Me: Right.
Them: And and why?
Me: Mhmm.
Them: Like, why And so, like, let me, first of all, show you that it's not. I can show you because seeing, like, real quality collapse in, you know, in in sort of domains other than the, like, couple that always get measured. Right? Okay. So we're seeing this quality collapse. So so why are we getting this quality collapse? Because the the kind of theoretical promise of speculative decoding is that it was gonna be lossless. But, like, what we're seeing is it's not so good. And why? But I I have an answer to the why.
Me: Answering the answer. Answering why is very hard.
Them: But yeah.
Me: Because if we go down the math wrong, I have to prove math mathematically why it's not a lossless. So and I don't know the answer for that. So I can yeah, I can only do the quality and the the token level validation here. Okay. So I think what should mean? I would I would definitely do the token level computation, see if we can find something concrete there. Yeah. Do you do you have any recommendation for the last paragraph, the multimodal part? Mhmm.
Them: Sorry. Hold on. Let me the multimodal part. Sorry. I was doing, I was doing I was doing I haven't gotten to that. I'm in the hands on lab. So I haven't gotten there.
Me: Do you think this tutorial is getting too deep? I'm also studying about it. I don't want you, like, getting it too deep than I I cannot even answer that. Because lots of the question you brought it up, I think is a very good question, but it's also beyond my reach.
Them: Yeah. I mean, I I don't know. I mean, part of it is I I don't exactly know what they're you know, I read the blog about what they're sort of looking for. But, you know, to be honest, the the blurb that they shared did not make a ton of sense to me. You know, they were like, hey. We want articles about the reprimetrization trick. But not about variational inference. And, like, those all come from, like, distinct categories in my mind. Those are, like, both you know,
Me: Ja,
Them: Fairly straightforward, like, mathematical like like, you know, is it just because one is called a trick? Like, the reprioritization trick isn't, like, a trick. It's like a mathematical identity. I I know. I, like, I didn't quite follow. So, you know, I think, hopefully, you
Me: Mhmm.
Them: Submit something, you get some, like, useful feedback and reviews about what they're looking for. You look at the sort of collection of things that got accepted and, you know, you target again, I guess I guess, like, high level, I think don't you know, this is sort of nicely wide ranging and covers you know, both both does sort of a, like, a review of the important kind of literature developments. You know, and an understanding of what's happening in practice, and some forward looking kind of future work. As well as kind of introducing like, I mean, it's doing a lot of things. I think I don't know if that's what they're looking for or they're looking for, like, like, a Chris Ola style super focused you know, interactive block. Like, I I don't know what they're looking for.
Me: I think I an e-mail and ask them about it. Confirm it.
Them: But no.
Me: I agree. They have I I think it has too much focus right now. I was
Them: Okay.
Me: Thinking I'll trim it down.
Them: I mean, I don't I don't think they know. Right? I think I think they've decided that they should do this new track and, like, they're gonna kinda figure it out on the fly.
Me: Yeah. I have confidence this will be accepted. It just I don't know whether this will be the best but it's fine. Yeah. I don't have to be the best.
Them: Sure, Lily. Sure.
Me: Thank you, Andrew. I know it's super late. They all tired? Really all the hard questions you brought. I I really enjoyed it. I will think more.
Them: No problem, Willie. I think this is really fun.
Me: Yeah.
Them: Alright.
Me: Thank you so much. Yeah. Okay. We can wrap up.
Them: Alright. I'll read the multimodal part real quick, and then I'm gonna go to bed.
Me: Yeah. Thank you so much. I appreciate it.
Them: Alright.
Me: Okay. Bye.
Them: See you.
Me: Okay. I'm in.
