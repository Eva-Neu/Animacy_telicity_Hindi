# Degrees of animacy and telicity in Hindi intransitives

## Background 

We investigate the semantic correlates of the unergative/unaccusative distinction using Hindi corpus data. Intransitives have been argued to fall into two classes: unergatives only have an
external, unaccusatives only an internal argument, with some verbs allowing for both structures (Burzio, 1986; Perlmutter, 1978). This syntactic distinction has been linked to semantic properties, in that strongly agentive arguments favour an unergative syntax, telic verb phrases an unaccusative syntax (e.g., Dowty, 1991). Sorace (2000) has argued that different verbs, by virtue of their lexical semantics, possess different degrees of animacy and telicity – e.g., ‘work’ is more agentive than ‘fall,’ ‘melt’ more telic than ‘run’ –, and that this predicts their likelihood to behave as unergatives or unaccusatives. Our goal is to test these claims against quantitative empirical measures.


## Methods

All data are taken from the Hindi Dependency Treebank.

Using animacy as a proxy for agentivity, we compute for each intransitive its probability of taking an animate argument. We first compile two lists of nouns: a) nouns in subject position bearing ergative case (highly likely to be animate) and b) nouns in direct object position not bearing direct object marking (highly likely to be inanimate) (Hindi_anim_1.py). After manually cleaning the lists, we then compute for each intransitive how often it takes a subject from one list and how often one from the other, thus arriving at an animacy score (Hindi_anim_2.py). 


Additionally, we compute how often each intransitive occurs with a light verb associated with a telic interpretation (a: ‘come’ or ja: ‘go’) (Hindi_tel.py).


## Bibliography 

Burzio, L. (1986). Italian syntax: A Government and Binding approach. D. Reidel. https://doi.org/https://doi.org/10.1007/978-94-009-4522-7

Dowty, D. (1991). Thematic proto-roles and argument selection. Language, 67, 547–619. https://doi.org/10.2307/415037

Perlmutter, D. (1978). Impersonal passives and the Unaccusative Hypothesis. Papers from the Annual Meeting of the Berkeley Linguistic Society, 4, 157–189. https://doi.org/10.3765/bls.v4i0.2198

Sorace, A. (2000). Gradients in auxiliary selection with intransitive verbs. Language, 76 (4), 859–890. https://doi.org/10.2307/417202
