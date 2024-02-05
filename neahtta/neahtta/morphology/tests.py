# Some misc test functions that need to be rewritten into actual tests


def sme_test():
    sme_options = {
        "compoundBoundary": "  + #",
        "derivationMarker": "suff.",
        "tagsep": " ",
        "inverse_tagsep": "+",
    }

    smexfst = XFST(
        lookup_tool="/Users/pyry/bin/lookup",
        fst_file="/Users/pyry/gtsvn/gt/sme/bin/n-sme.fst",
        ifst_file="/Users/pyry/gtsvn/gt/sme/bin/isme.fst",
        options=sme_options,
    )

    sme = smexfst >> Morphology("sme")

    return sme


def sme_test_restrictions():
    sme_options = {
        "compoundBoundary": "  + #",
        "derivationMarker": "suff.",
        "tagsep": " ",
        "inverse_tagsep": "+",
    }

    smexfst = XFST(
        lookup_tool="/Users/pyry/bin/lookup",
        fst_file="/Users/pyry/gtsvn/gt/sme/bin/n-sme.fst",
        ifst_file="/Users/pyry/gtsvn/gt/sme/bin/isme.fst",
        options=sme_options,
    )

    sme = smexfst >> Morphology("sme")

    return sme


def sme_restricted_generation():
    sme = sme_test()
    sme_restr = sme_test_restrictions()

    test_words = [
        "mannat",
        # u'dahkat'
    ]
    test_tags = [
        "V+Ind+Prs+Sg1".split("+"),
        "V+Ind+Prs+Sg2".split("+"),
        "V+Ind+Prs+Sg3".split("+"),
        "V+Ind+Prt+Sg3".split("+"),
        "V+Ind+Prs+Pl3".split("+"),
        "V+Ind+Prt+Pl3".split("+"),
    ]
    print("restricted")
    for w in test_words:
        gens = sme.generate(w, test_tags, False)
        print(w)
        for l in gens:
            if l[2]:
                for f in l[2]:
                    print("\t" + f + "\t" + "+".join(l[1]))
            else:
                print("\t" + "NOPE")

    print("unrestricted")
    for w in test_words:
        gens = sme_restr.generate(w, test_tags, False)
        print(w)
        for l in gens:
            if l[2]:
                for f in l[2]:
                    print("\t" + f + "\t" + "+".join(l[1]))
            else:
                print("\t" + "NOPE")


def sme_derivation_test():
    sme = sme_test()

    test_words = ["borahuvvat", "juhkaluvvan"]
    for w in test_words:
        print("No options")
        print(sme.lemmatize(w))

        print("/lookup/ lemmatizer")
        print(
            sme.lemmatize(
                w, split_compounds=True, non_compound_only=True, no_derivations=True
            )
        )


def sme_compound_test():
    # TODO: make UnitTests out of these.
    sme = sme_test()

    print("No options")
    print(sme.lemmatize("báhčinsearvi"))

    print("Strip derivation, compounds, but also split compounds")
    print(
        sme.lemmatize(
            "báhčinsearvi",
            split_compounds=True,
            non_compound_only=True,
            no_derivations=True,
        )
    )

    print("Strip derivation, but also split compounds")
    print(sme.lemmatize("báhčinsearvi", split_compounds=True, no_derivations=True))

    print("Strip compounds, but also split compounds")
    print(sme.lemmatize("báhčinsearvi", split_compounds=True, non_compound_only=True))

    print("Strip compounds")
    print(sme.lemmatize("báhčinsearvi", non_compound_only=True))

    print("Split compounds")
    print(sme.lemmatize("báhčinsearvi", split_compounds=True))

    print(
        sme.lemmatize(
            "boazodoallošiehtadallanlávdegotti",
            split_compounds=True,
            non_compound_only=True,
            no_derivations=True,
        )
    )


def examples():
    # TODO: make this into tests

    obt = OBT("/Users/pyry/gtsvn/st/nob/obt/bin/mtag-osx64")

    nob = obt >> Morphology("nob")
    print()
    print(" -- nob --")
    print(" ingen: ")
    for a in nob.lemmatize("ingen"):
        print("  " + a)

    print(" tålt: ")
    for a in nob.lemmatize("tålt"):
        print("  " + a)

    sme = sme_test()
    print()
    print(" -- sme lemmatize --")
    print(" mánnat: ")
    for a in sme.lemmatize("mannat"):
        print("  " + a)

    generate = sme.generate(
        "mannat",
        [
            ["V", "Inf"],
            ["V", "Ind", "Prs", "Sg1"],
            ["V", "Ind", "Pst", "Sg2"],
            ["V", "Ind", "Prt", "Sg2"],
        ],
    )

    for lem, tag, forms in generate:
        if forms:
            for form in forms:
                print("  " + " ".join(tag) + " => " + form)
        else:
            print("  " + " ".join(tag) + ":   unknown")

    generate = sme.generate(
        "eaktodáhtolašš",
        [
            ["A", "Attr"],
        ],
    )

    for lem, tag, forms in generate:
        if forms:
            for form in forms:
                print("  " + " ".join(tag) + " => " + form)
        else:
            print("  " + " ".join(tag) + ":   unknown")

    print(" -- lemmatize -- ")
    for a in sme.lemmatize("spábbačiekčangilvu"):
        print("  " + a)

    print(" -- lemmatize with compounds -- ")
    for a in sme.lemmatize("juovlaspábbačiekčangilvu", split_compounds=True):
        print("  " + a)

    print(" -- lemmatize -- ")
    for a in sme.lemmatize("juovlaspábbačiekčangilvu"):
        print("  " + a)


def tag_examples():
    setdefs = {
        "type": ["NomAg", "G3"],
        "person": ["Sg1", "Sg2", "Sg3"],
    }

    tagsets = Tagsets(setdefs)
    tag_test = Tag("N+NomAg+Sg+Ill", sep="+")
    print(tag_test)

    _type = tagsets["type"]
    for m in _type.members:
        print(m)

    print(tag_test.getTagByTagset(_type))
    print(tag_test[_type])

    for item in tag_test:
        print(item)


if __name__ == "__main__":
    # examples()
    # tag_examples()
    # sme_compound_test()
    # sme_derivation_test()
    sme_restricted_generation()
