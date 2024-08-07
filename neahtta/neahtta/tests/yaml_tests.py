import os
import sys
import tempfile
import unittest

import yaml

import neahtta
from termcolor import colored
from flask import current_app

tests_module = os.path.join(os.getcwd(), "tests/")

projname = (
    os.environ["NDS_CONFIG"].partition("configs/")[2].partition(".config.yaml")[0]
)

project_test_file = os.path.join(tests_module, projname + ".yaml")


class Failures(object):
    def __init__(self):
        self.failure_list = []

    def add(self, test, exception, _input, expect, result, msg=""):
        self.failure_list.append((test, exception, _input, expect, result, msg))

    def summarize(self):
        print(self.failure_list)


failuretrack = Failures()


class YamlTests(object):
    def __init__(self, path):
        self.filename = path

        with open(self.filename, "r") as F:
            self.yaml = yaml.load(F, yaml.Loader)

    @property
    def request_tests(self):
        if not self.yaml.get("RequestTests"):
            return []
        cases = []
        for case_def in self.yaml.get("RequestTests"):
            # a little more processing will happen here
            uri = case_def.get("uri")
            for test in case_def.get("tests"):
                case = []
                case.append(uri)
                case.append(test)
                cases.append(case)
        return cases

    @property
    def morpholexicon_tests(self):
        if not self.yaml.get("MorpholexicalAnalysis"):
            return []
        cases = []
        for case_def in self.yaml.get("MorpholexicalAnalysis"):
            mlex = tuple(case_def.get("morpholexicon"))
            for test in case_def.get("tests"):
                case = []
                case.append(mlex)
                case.append(test)
                cases.append(case)
        return cases

    @property
    def morpholexical_generation_tests(self):
        if not self.yaml.get("MorpholexicalGeneration"):
            return []
        cases = []
        for case_def in self.yaml.get("MorpholexicalGeneration"):
            mlex = tuple(case_def.get("morpholexicon"))
            for test in case_def.get("tests"):
                case = []
                case.append(mlex)
                case.append(test)
                cases.append(case)
        return cases

    @property
    def lexicon_definition_tests(self):
        if not self.yaml.get("Lexicon"):
            return []

        cases = []
        for case_def in self.yaml.get("Lexicon"):
            mlex = tuple(case_def.get("lexicon"))
            for test in case_def.get("tests"):
                case = []
                case.append(mlex)
                case.append(test)
                cases.append(case)
        return cases


class NDSInstance(unittest.TestCase):
    """Setup and teardown for NDS:"""

    def context(self):
        return self.current_app.test_request_context("?")

    def setUp(self):
        _app = neahtta.app
        _app.debug = True
        _app.logger.removeHandler(_app.logger.smtp_handler)

        _app.caching_enabled = False
        self.app = _app.test_client()
        self.current_app = _app

        self.yamltests = YamlTests(project_test_file)

    def tearDown(self):
        # failuretrack.summarize()
        pass


# TODO: print useful text about process
class RequestTest(NDSInstance):
    """These are defined in the .yaml file as:

    RequestTests:
     - etc.
    """

    def test_requests(self):
        from cssselect import GenericTranslator, SelectorError
        from lxml.html.soupparser import fromstring

        print("Running RequestTests tests...")
        print("(Expect to find certain strings in generated HTML)")

        for uri, case in self.yamltests.request_tests:
            uri_formatted = uri % case.get("uri_args")
            expected = case.get("expected_values")
            value_selector = case.get("value_selector")

            print("  uri:   " + colored(uri_formatted, "cyan"))
            print("  select:  " + colored(value_selector, "cyan"))
            print("  expect:  " + colored(" ".join(expected), "cyan"))

            # Run the mock request
            response = self.app.get(uri_formatted)

            # Parse the tree by the test definition, and compare
            tree = fromstring(response.data)
            expr = GenericTranslator().css_to_xpath(value_selector)
            selected = [a.text for a in tree.xpath(expr)]
            print("  result:  " + colored(" ".join(selected), "magenta"))

            for e in expected:
                try:
                    self.assertIn(e, selected)
                except Exception as exc:
                    print("    " + colored("FAILED", "red") + ": " + e)
                    print("     > " + colored("Values not found in selector", "yellow"))
                    failuretrack.add(
                        "RequestTest",
                        exc,
                        "%s [%s]" % (uri_formatted, value_selector),
                        " ".join(expected),
                        " ".join(selected),
                        "Values not found in selector",
                    )
                else:
                    print("    " + colored("PASSED", "green") + " (" + e + ")")

            print("")


# TODO: print useful text about process
class MorpholexicalAnalysis(NDSInstance):
    """These are defined in the .yaml file as:

    MorpholexicalAnalysis:
     - etc.
    """

    def test_morpholexical_analyses(self):
        skw = {
            "split_compounds": True,
            "non_compounds_only": False,
            "no_derivations": False,
            "return_raw_data": True,
        }

        # TODO: print useful text
        with self.context():
            print("Running MorpholexicalAnalysis tests...")
            print("(Expect lemmas for input forms)")

            m = self.current_app.morpholexicon
            for (source, target), case in self.yamltests.morpholexicon_tests:
                expect = case.get("expected_lemmas")

                res, raw_out, raw_err = m.lookup(
                    case.get("input"), source_lang=source, target_lang=target, **skw
                )

                description = case.get("description", False)
                if description:
                    print("  " + colored(description, "yellow"))

                print("  input:   " + colored(case.get("input"), "cyan"))

                lemmas = [r.lemma for r in res.analyses]

                print("  expect:  " + colored(" ".join(expect), "cyan"))
                print("  result:  " + colored(" ".join(lemmas), "magenta"))

                for e in expect:
                    try:
                        self.assertIn(e, lemmas)
                    except Exception as exc:
                        print("    " + colored("FAILED", "red") + ": " + e)
                        failuretrack.add(
                            "MorphologicalAnalysis",
                            exc,
                            case.get("input"),
                            " ".join(expect),
                            " ".join(lemmas),
                        )
                    else:
                        print("    " + colored("PASSED", "green") + " (" + e + ")")

                print("")


# TODO: failure summary ? how best to raise errors
class MorpholexicalGeneration(NDSInstance):
    """These are defined in the .yaml file as:

    ParadigmGenerationThroughMorpholexicon:
     - etc.
    """

    def test_morpholexical_generation(self):
        skw = {
            "split_compounds": True,
            "non_compounds_only": False,
            "no_derivations": False,
            "return_raw_data": True,
        }

        def test_the_case(case, result, _input=""):
            expect = case.get("expected_forms", False)
            unexpect = case.get("unexpected_forms", False)

            if expect:
                test_func = self.assertIn
                msg = "Form not generated."
                _in = expect
                print("  expect:  " + colored(repr(expect), "cyan"))
                print("  result:  " + colored(" ".join(result), "magenta"))

            if unexpect:
                test_func = self.assertNotIn
                msg = "Generated form appeared that shouldn't."
                _in = unexpect

                print("  DONT expect: " + colored(repr(expect), "cyan"))
                print("  result:      " + colored(" ".join(result), "magenta"))

            if not expect and not unexpect:
                _in = []
                print(colored("  Not expecting any result.", "yellow"))
                print("  result:      " + colored(" ".join(result), "magenta"))

            for e in _in:
                try:
                    test_func(e, result, msg)
                except Exception as exc:
                    print("    " + colored("FAILED", "red") + ": " + e)
                    # TODO: something else with this
                    # print debug
                    print("     > " + colored(msg, "yellow"))
                    failuretrack.add(
                        "MorphologicalGeneration",
                        exc,
                        _input,
                        " ".join(expect),
                        " ".join(result),
                        msg,
                    )
                print("    " + colored("PASSED", "green") + " (" + e + ")")

        # TODO: print useful text
        with self.context():
            print("Running MorpholexicalGeneration tests...")
            print("(Expect generated forms for lemma from input forms)")

            m = self.current_app.morpholexicon
            for (source, target), case in self.yamltests.morpholexical_generation_tests:
                expect = case.get("expected_forms", False)
                unexpect = case.get("unexpected_forms", False)

                description = case.get("description", False)
                if description:
                    print("  " + colored(description, "yellow"))

                print("  input:   " + colored(case.get("input"), "cyan"))

                res, raw_out, raw_err = m.lookup(
                    case.get("input"), source_lang=source, target_lang=target, **skw
                )

                for node, morph_analyses in res:
                    if node is not None:
                        paradigm, debug = self.generate_paradigm(
                            source, node, morph_analyses
                        )
                        result = [g.form for g in paradigm]

                        test_the_case(case, result, _input=case.get("input"))
                        # TODO: set a success value?

                print("")

    def generate_paradigm(self, lang, node, morph_analyses):
        current_app = self.current_app

        debug_text = ""

        _str_norm = "string(normalize-space(%s))"

        morph = current_app.config.morphologies.get(lang, False)
        mlex = current_app.morpholexicon

        paradigm_from_file, paradigm_template = mlex.paradigms.get_paradigm(
            lang, node, morph_analyses, return_template=True
        )

        generated_and_formatted = []

        l = node.xpath("./lg/l")[0]
        lemma = l.xpath(_str_norm % "./text()")

        if paradigm_from_file:
            extra_log_info = {
                "template_path": paradigm_template,
            }
            form_tags = [_t.split("+")[1::] for _t in paradigm_from_file.splitlines()]
            # TODO: bool not iterable
            _generated, _stdout, _stderr = morph.generate_to_objs(
                lemma,
                form_tags,
                node,
                extra_log_info=extra_log_info,
                return_raw_data=True,
            )
        else:
            # For pregenerated things
            _generated, _stdout, _stderr = morph.generate_to_objs(
                lemma, [], node, return_raw_data=True
            )

        debug_text += "\n\n" + _stdout + "\n\n"

        return _generated, debug_text


# TODO: failure summary ? how best to raise errors
class LexiconDefinitions(NDSInstance):
    """These are defined in the .yaml file as:

    LexiconDefinitions:
     - etc.
    """

    def test_lexicon_definitions(self):
        skw = {
            "split_compounds": True,
            "non_compounds_only": False,
            "no_derivations": False,
            "return_raw_data": True,
        }

        _str_norm = "string(normalize-space(%s))"

        def test_the_case(case, result):
            # test multiple results

            expect_in = case.get("expected_definitions", False)
            unexpect_in = case.get("unexpected_definitions", False)

            if expect_in:
                test_func = self.assertIn
                err_msg = "Could not find definition."
                _in = expect_in
                print("  expect:  " + colored(repr(_in), "cyan"))
                print("  result:  " + colored(repr(result), "magenta"))

            if unexpect_in:
                test_func = self.assertNotIn
                err_msg = "Unexpected definition."
                _in = unexpect_in
                print("  DONT expect: " + colored(repr(_in), "cyan"))
                print("  result:      " + colored(repr(result), "magenta"))

            if not expect_in and not unexpect_in:
                _in = []
                print(colored("  Not expecting any result.", "yellow"))
                print("  result:      " + colored(repr(result), "magenta"))
                print("    " + colored("PASSED", "green"))

            for _i in _in:
                try:
                    test_func(_i, result)
                except Exception as exc:
                    print("    " + colored("FAILED", "red") + ": " + repr(_i))
                    if err_msg:
                        print("     > " + colored(err_msg, "yellow"))
                    failuretrack.add(
                        "LexiconDefinitions",
                        exc,
                        _i,
                        " ".join(_in),
                        " ".join(result),
                        err_msg,
                    )
                else:
                    print("    " + colored("PASSED", "green"))

        with self.context():
            m = self.current_app.morpholexicon

            print("Running Lexicon tests...")

            for (source, target), case in self.yamltests.lexicon_definition_tests:
                translation_xpath = case.get("xpath", "./mg/tg/t/text()")

                description = case.get("description", False)
                if description:
                    print("  " + colored(description, "yellow"))

                print("  input:   " + colored(case.get("input"), "cyan"))
                print("  xpath:   " + colored(translation_xpath, "cyan"))

                res, raw_out, raw_err = m.lookup(
                    case.get("input"), source_lang=source, target_lang=target, **skw
                )

                successes = False
                for node, morph_analyses in res:
                    if node is None:
                        continue
                    else:
                        successes = True

                    result_defs = node.xpath(_str_norm % translation_xpath)

                    test_the_case(case, result_defs)
                    # TODO: set a success value?

                if not successes:
                    err_msg = "No results found for input."

                    print(
                        "    "
                        + colored("FAILED", "red")
                        + ": "
                        + repr(case.get("input"))
                    )
                    print("     > " + colored(err_msg, "yellow"))
                    failuretrack.add(
                        "LexiconDefinitions",
                        "",
                        case.get("input"),
                        "",
                        "",
                        err_msg,
                    )

                print("")
