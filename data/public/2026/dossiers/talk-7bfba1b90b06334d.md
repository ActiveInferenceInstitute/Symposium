# A Modular Perspective Layer for Active Inference Agents

Presenter: Hongju Pae

Contribution: Interactive Workshop

Public ID: talk&#45;7bfba1b90b06334d

## Submitted abstract

Most agent architectures collapse two things that phenomenology keeps apart&#58; what the agent should do immediately&#44; and what kind of world the agent takes itself to be in&#46; This session introduces &#8220;perspective&#8221; as a distinct architectural layer that carries the second&#46; 
Perspective is a slowly evolving&#44; history&#45;sensitive latent state that gates how observations are encoded&#46; Importantly&#44; it is decoupled from policy gradients and is never itself an optimization target&#46; Because it is decoupled&#44; it is portable and can be attached on top of an existing policy&#45;optimizing agent rather than requiring a bespoke design&#46;
The first part of the session develops the conceptual frame&#58; how a phenomenologically motivated condition translates into a concrete architectural commitment&#44; and why that commitment is orthogonal to belief&#45;state inference and policy selection&#46; I then trace the capabilities that this single layer has been shown to support across a sequence of studies&#44; including directional hysteresis&#44; history&#45;dependent perceptual reorganization&#44; and body&#45;grounded conative orientation&#44; treating these as unified aspects of a single portable module&#46;
There will then be a live demonstration attaching the perspective layer to an active inference agent&#44; such as a hierarchical Bayesian &#47; discrete state&#45;space model&#44; and running it in parallel with its unaugmented counterpart in the same environment&#44; so participants can see exactly what the layer adds and where it plugs in&#46;
The session closes with a structured discussion in which participants are invited to identify candidate insertion points for a perspective layer in their own active inference agents&#44; whether built in PyMDP&#44; RxInfer&#44; or custom frameworks&#46; The aim is to leave participants able to reason about whether and how a subjective perspective could be added&#46;

Source: [submitted source](<https://2026symposium.activeinference.institute/>)

Abstract SHA256: 52989bb421dddd9c78c2b4a2d77e98d7e180d842e16e392fbfad17a36a1a7413

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

OpenAlex discovery-only search (not a verified identity or literature match): https&#58;&#47;&#47;openalex&#46;org&#47;works&#63;search&#61;A&#37;20Modular&#37;20Perspective&#37;20Layer&#37;20for&#37;20Active&#37;20Inference&#37;20Agents
