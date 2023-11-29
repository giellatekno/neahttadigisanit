# User friendly tag relabeling

    configs/language_specific_rules/user_friendly_tags/*.relabel

Each file is named with a suffix `.relabel`, but the name may be
anything. Organize tag relabel sets however you will, maybe on a
language-pair to language-pair basis, or by dictionary set instead.

Consider that you may have to repeat some tagsets, so maybe using YAML
aliases will make things easier.

## File structure

The file structure is quite simple, and at most it must contain a list
called `Relabel`. Each list item is a dictionary containing the keys:

 * **source_morphology** - The morphology name, usually an ISO, but
   sometimes something else in the case of language variants. (`sme`,
   `SoMe`, `kpv`)
 * **target_ui_language** - The language the user is browsing in-- must
   be an ISO.
 * **tags** - A dictionary of tags.

### Example

    Relabel:

      - source_morphology: 'kpv'
        target_ui_language: 'eng'
        tags: &some_alias_name
          V: "v."
          N: "n."
          A: "adj."

      - source_morphology: 'kpv'
        target_ui_language: 'fin'
        tags: &another_alias
          V: "v."
          N: "s."
          A: "adj."
          DO_NOT_SHOW: ""

      - source_morphology: "zzz"
        target_ui_language: "www"
        tags:
          <<: *some_alias_name
          <<: *another_alias

The last item in the list shows an example of inheriting from two
sources. Thus, the resulting tags will be:

          V: "v."
          N: "s."
          A: "adj."
          DO_NOT_SHOW: ""

You can even set tags in another location, outside of the `Relabel`
list, if necessary.

    Aliases:
      tag_set_one: &some_alias_name
        V: "v."
        N: "n."
        A: "adj."

    Relabel:
      - source_morphology: 'kpv'
        target_ui_language: 'eng'
        tags: 
          <<: *some_alias_name

