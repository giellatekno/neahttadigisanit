from flask import current_app, g


def register_template_filters(app):
    # An idea, if specific forms need to be generated
    # however, for this to be available from context files, some
    # changes need to be made: context management should be moved from
    # config.py to TemplateConfig.

    # @app.template_filter('generate_form')
    # def generate_form(lemma, tags):
    #     print lemma, tags
    #     extra_log_info = {
    #         'template_path': 'generate_form filter',
    #     }
    #     if type(tags) != list:
    #         tags = [tags]

    #     generate_tags = []
    #     for t in tags:
    #         # use morph tagsep function
    #         generate_tags.append(t.split('+'))

    #     morph = current_app.config.morphologies.get(g._from, False)
    #     print lemma, generate_tags
    #     forms = morph.generate(lemma, generate_tags, None,
    #                            extra_log_info=extra_log_info)

    #     return forms

    @app.template_filter()
    def hash_node(node):
        # anders: path change
        from neahtta.nds_lexicon.lexicon import hash_node

        return hash_node(node)

    @app.template_filter()
    def render_block(template, block):
        """Used to generate doc"""
        c = template.new_context(vars={"TEMPLATE_DOC": True})
        return "".join(line for line in block(c))

    @app.template_filter()
    def template_lines(template):
        return "".join(line for line in template.stream())

    @app.template_filter()
    def group_by_tag(forms):
        """Group a list of GeneratedForms by the tag, and return a list
        of lists
        """
        from itertools import groupby
        from operator import itemgetter

        # For some reason groupby with a key function did not work for
        # this...

        tag_by_form = [(g.tag.tag_string, g) for g in forms]
        groups = groupby(tag_by_form, itemgetter(0))
        forms = [list(map(itemgetter(1), b)) for a, b in groups]

        return forms

    @app.template_filter()
    def remove_by_tagset(tag_as_list, tagset_name):
        try:
            m = current_app.config.morphologies[g._from]
        except KeyError:
            return tag_as_list

        try:
            filter_set = m.tagsets[tagset_name]
        except KeyError:
            return tag_as_list

        return [t for t in tag_as_list if t not in filter_set]

    @app.template_filter()
    def by_tagset(generated_forms, tagset_name):
        fs = []
        for x in generated_forms:
            if x.tag[tagset_name]:
                fs.append(x)
        return fs

    @app.template_filter()
    def by_tagset_value(generated_forms, tagset_name, tagset_value):
        fs = []
        for x in generated_forms:
            if x.tag[tagset_name]:
                if x.tag[tagset_name] == tagset_value:
                    fs.append(x)
        return fs

    @app.template_filter()
    def without_tagset(generated_forms, tagset_name):
        fs = []
        for x in generated_forms:
            if not x.tag[tagset_name]:
                fs.append(x)
        return fs

    @app.template_filter()
    def insert_value(generated_forms, position, value):
        generated_forms.insert(position, value)
        return generated_forms

    @app.template_filter()
    def xpath(node_obj, xpath_str):
        if node_obj is not None:
            return node_obj.xpath(xpath_str)

    @app.template_filter()
    def sortby_xpath(node_objs, xpath_str, value_type="int"):
        _str_norm = "string(normalize-space(%s))"

        def get_xp(n):
            try:
                v = n.xpath(_str_norm % xpath_str)
            # anders: which exceptions are we catching here?
            except Exception:
                v = False
            if value_type == "int":
                try:
                    v = int(v)
                except ValueError:
                    pass
            return v

        return sorted(node_objs, key=get_xp)

    @app.template_filter()
    def xpath_first(node_obj, xpath_str):
        n = node_obj.xpath(xpath_str)
        if n is not None:
            if len(n) > 0:
                return n[0]
        return False

    @app.template_filter("text")
    def xpath_text(n):
        if n is not None:
            return n.text
        else:
            return False

    @app.template_filter()
    def xpath_first_text(node_obj, xpath_str):
        n = xpath_first(node_obj, xpath_str)
        if n is not None:
            return n.text
        else:
            return False

    @app.template_filter()
    def generate_or_not(lemma, iso, tag, entry=None):
        mx = current_app.config.morphologies.get(iso)

        if mx is None:
            return lemma, ""

        # anders: unused
        # tagsep = mx.tool.options.get("inverse_tagsep")
        dummy = mx.tagsets.sets.get("nds_dummy_tags", [])

        # TODO: strip nds_dummy_tags
        tag_string = []
        for tp in tag.parts:
            if tp == lemma:
                continue
            if tp in dummy:
                continue
            tag_string.append(tp)

        # TODO: PV/e tags cause problems because they have been shifted
        # to the right of the lemma. maybe the tag processor function
        # needs to fix this

        try:
            generated, raw_out, raw_errors = mx.generate(
                lemma, [tag_string], entry, template_tag=True
            )
        except Exception:
            generated, raw = False, ""

        if generated:
            forms = []
            for a in generated:
                if len(a) == 2:
                    gener_fs = a[1]
                    if gener_fs:
                        for f in gener_fs:
                            forms.append(f)

            raw = raw_out + raw_errors
        else:
            forms = [lemma]
            raw = ""

        return forms, raw

    @app.template_filter()
    def console_log(string):
        s = string.strip().encode("unicode-escape")
        return f'<script type="text/javascript">console.log("{s}")</script>'
