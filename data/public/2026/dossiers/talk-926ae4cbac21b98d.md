# VAMAI&#58; Variational Affordance Mapping and Active Inference for Training&#45;Free UAV Navigation

Presenter: Harshil Shah&#44; Satyaki Maitra

Contribution: Pre&#45;recorded Video presentation

Public ID: talk&#45;926ae4cbac21b98d

## Submitted abstract

We present VAMAI &#40;Variational Affordance Mapping and Active Inference&#41;&#44; a training&#45;free hierarchical framework for autonomous UAV navigation in partially observed environments where reliable GPS may be unavailable&#46; VAMAI brings together affordance theory&#44; probabilistic environmental modeling&#44; and active inference to address how an autonomous agent can navigate while continually learning about its surroundings&#46;
VAMAI connects geometric perception to the question of which actions the environment affords the drone&#46; It maintains probabilistic beliefs over possible obstacle configurations&#44; updated through LiDAR and depth&#45;sensing observations&#46; From these beliefs&#44; the system derives regional suitability estimates describing whether passages are blocked&#44; constrained&#44; or sufficiently open for traversal&#46;
For decision&#45;making under uncertainty&#44; Expected Free Energy &#40;EFE&#41;&#45;based planning evaluates candidate movements using goal progress&#44; regional suitability&#44; and the expected information gain of future observations across spatial regions&#46; At the local level&#44; a separate motion&#45;planning and control system translates selected intentions into dynamically feasible trajectories&#44; accounting for obstacles&#44; vehicle motion&#44; and evolving environmental beliefs&#46;
We will illustrate this process through simulation examples&#44; tracing how sensor observations influence environmental beliefs&#44; regional navigation decisions&#44; and continuous flight execution&#46; We will also discuss the computational and architectural challenges of coordinating perception&#44; inference&#44; planning&#44; and control as independently progressing components&#44; and how these considerations shape the development of a scalable active inference navigation system&#46;

Source: [submitted source](<https://2026symposium.activeinference.institute/>)

Abstract SHA256: de462961da948aa635ce4424887e812ec325edb9952a55082776735f2755e86f

## Organizer review checklist

- [ ] Confirm the submitted title, presenter, and abstract with the presenter.
- [ ] Confirm contribution format and scheduling needs.
- [ ] Confirm public permissions for any additional material before publication.
- [ ] Prepare discussion questions grounded in the submitted abstract.

## Public learning resources

These approved event resources are starting points; topic relevance and author identity have not been inferred.

- Active Inference Ontology: https&#58;&#47;&#47;github&#46;com&#47;ActiveInferenceInstitute&#47;Active&#95;Inference&#95;Ontology
- Cognitive Agent Modeling: https&#58;&#47;&#47;github&#46;com&#47;ActiveInferenceInstitute&#47;ActiveInferenceImplementations
- GEO&#45;INFER: https&#58;&#47;&#47;github&#46;com&#47;ActiveInferenceInstitute&#47;GEO&#95;INFER
- Generalized Notation Notation: https&#58;&#47;&#47;github&#46;com&#47;ActiveInferenceInstitute&#47;Generalized&#95;Notation&#95;Notation
- pymdp: https&#58;&#47;&#47;github&#46;com&#47;infer&#45;actively&#47;pymdp
- Reproducible publication template: https&#58;&#47;&#47;github&#46;com&#47;docxology&#47;template

OpenAlex discovery-only search (not a verified identity or literature match): https&#58;&#47;&#47;openalex&#46;org&#47;works&#63;search&#61;VAMAI&#37;3A&#37;20Variational&#37;20Affordance&#37;20Mapping&#37;20and&#37;20Active&#37;20Inference&#37;20for&#37;20Training&#45;Free&#37;20UAV&#37;20Navigation
