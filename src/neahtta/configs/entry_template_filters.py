from flask import current_app
from flask import g

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

    @app.template_filter('hash_node')
    def hash_node(node):
        from lexicon.lexicon import hash_node
        return hash_node(node)

    @app.template_filter('group_by_tag')
    def group_by_tag(forms):
        """ Group a list of GeneratedForms by the tag, and return a list
        of lists
        """
        from itertools import groupby
        from operator import itemgetter

        # For some reason groupby with a key function did not work for
        # this... 

        tag_by_form = [(g.tag.tag_string, g) for g in forms]
        groups = groupby( tag_by_form, itemgetter(0))
        forms = [map(itemgetter(1), b) for a, b in groups]

        return forms

    @app.template_filter('by_tagset')
    def by_tagset(generated_forms, tagset_name):
        fs = []
        for g in generated_forms:
            if g.tag[tagset_name]:
                fs.append(g)
        return fs

    @app.template_filter('by_tagset_value')
    def by_tagset_value(generated_forms, tagset_name, tagset_value):
        fs = []
        for g in generated_forms:
            if g.tag[tagset_name]:
                if g.tag[tagset_name] == tagset_value:
                    fs.append(g)
        return fs

    @app.template_filter('without_tagset')
    def without_tagset(generated_forms, tagset_name):
        fs = []
        for g in generated_forms:
            if not g.tag[tagset_name]:
                fs.append(g)
        return fs

    @app.template_filter('xpath')
    def xpath(node_obj, xpath_str):
        if node_obj is not None:
            return node_obj.xpath(xpath_str)
        else:
            return None

    @app.template_filter('xpath_first')
    def xpath_first(node_obj, xpath_str):
        n = node_obj.xpath(xpath_str)
        if n is not None:
            if len(n) > 0:
                return n[0]
        return False

    @app.template_filter('text')
    def xpath_text(n):
        if n is not None:
            return n.text
        else:
            return False

    @app.template_filter('xpath_first_text')
    def xpath_first_text(node_obj, xpath_str):
        n = xpath_first(node_obj, xpath_str)
        if n is not None:
            return n.text
        else:
            return False

    return app

