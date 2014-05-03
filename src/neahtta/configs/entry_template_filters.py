
def register_template_filters(app):

    @app.template_filter('by_tagset')
    def by_tagset(generated_forms, tagset_name):
        for g in generated_forms:
            if g.tag[tagset_name]:
                yield g

    @app.template_filter('by_tagset_value')
    def by_tagset_value(generated_forms, tagset_name, tagset_value):
        for g in generated_forms:
            if g.tag[tagset_name]:
                if g.tag[tagset_name] == tagset_value:
                    yield g

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

