def iso_filter(_iso):
    """ These things are sort of a temporary fix for some of the
    localization that runs off of CSS selectors, in order to include the
    3 digit ISO into the <body /> @lang attribute.
    """
    from configs.language_names import ISO_TRANSFORMS
    return ISO_TRANSFORMS.get(_iso, _iso)

DEBUG = False

# TODO: doesn't recognize translation comments yet, but I'm not really
# in need of these
# TODO: in order to work this needs to be a legit python package, 
#  http://babel.edgewall.org/wiki/Documentation/0.9/messages.html#id1
# TODO: line numbers seem to be off
def extract_yaml(fileobj, keywords, comment_tags, options):
    """Extract messages from YAML source code.

    :param fileobj: the seekable, file-like object the messages should be
                    extracted from
    :param keywords: a list of keywords (i.e. function names) that should be
                     recognized as translation functions
    :param comment_tags: a list of translator tags to search for and include
                         in the results
    :param options: a dictionary of additional options (optional)
    """
    from babel.messages.jslexer import tokenize, unquote_string
    from yamllex import YAMLLexer

    yaml_lexer = YAMLLexer()

    tokenize = yaml_lexer.get_tokens

    funcname = message_lineno = None
    messages = []
    last_argument = None
    translator_comments = []
    concatenate_next = False
    encoding = options.get('encoding', 'utf-8')
    last_token = None
    call_stack = -1

    linecount = 0
    token_line_no = 0
    for _type, value in tokenize(fileobj.read().decode(encoding)):
        token_type = str(_type)
        # if value.find('gettext') > -1:
        #     print keywords.keys()
        #     print call_stack
        #     print token_type, value
        #     print linecount
        #     print message_lineno
        #     print 
        # Token.Text.Break '\n
        # Token.Text.Blank
        # Token.Literal.Scalar.Flow.Quote
        # Token.Literal.Scalar.Flow

        # Token.Name.Type u'!gettext'
        # Token.Text.Blank
        # Token.Literal.Scalar.Flow.Quote
        # Token.Literal.Scalar.Flow
        # Token.Literal.Scalar.Flow
        # Token.Literal.Scalar.Flow.Quote
        # Token.Text.Break '\n'

        if token_type == 'Token.Text.Break':
            linecount += 1
            call_stack = -1

        elif token_type == 'Token.Text.Blank':
            if funcname:
                if DEBUG: print call_stack, "  in function   ", value
                message_lineno = linecount
                call_stack += 1

        elif token_type == 'Token.Literal.Scalar.Flow.Quote':
            if funcname:
                if DEBUG: print call_stack, "  function quote      ", value
                concatenate_next = True
                if concatenate_next and call_stack == 1:
                    concatenate_next = False
                    if DEBUG: print new_value
                message_lineno = linecount
                call_stack += 1

        elif call_stack == -1 and token_type == 'Token.Comment.Single':
            value = value[2:].strip()
            if translator_comments and \
               translator_comments[-1][0] == token.lineno - 1:
                translator_comments.append((token.lineno, value))
                continue

            for comment_tag in comment_tags:
                if value.startswith(comment_tag):
                    translator_comments.append((token.lineno, value.strip()))
                    break

        # The yaml lexer doesn't recognize multiline comments, so, fun
        # times

        # elif token_type == 'multilinecomment':
        #     # only one multi-line comment may preceed a translation
        #     translator_comments = []
        #     value = value[2:-2].strip()
        #     for comment_tag in comment_tags:
        #         if value.startswith(comment_tag):
        #             lines = value.splitlines()
        #             if lines:
        #                 lines[0] = lines[0].strip()
        #                 lines[1:] = dedent('\n'.join(lines[1:])).splitlines()
        #                 for offset, line in enumerate(lines):
        #                     translator_comments.append((token.lineno + offset,
        #                                                 line))
        #             break

        elif funcname and call_stack == 1:
            if token_type == 'Token.Literal.Scalar.Flow.Quote':
                if DEBUG:
                    print call_stack, 'funcname, got quote'
                    print new_value

                # if last_argument is not None:
                #     print '  last arg'
                #     messages.append(last_argument)
                #     last_argument = ''
                # if len(messages) > 1:
                #     messages = tuple(messages)
                # elif messages:
                #     messages = messages[0]
                # else:
                #     messages = None

                # Comments don't apply unless they immediately precede the
                # message
                if translator_comments and \
                   translator_comments[-1][0] < message_lineno - 1:
                    translator_comments = []

                if messages is not None:
                    yield (message_lineno, funcname, messages,
                           [comment[1] for comment in translator_comments])

                funcname = message_lineno = last_argument = None
                concatenate_next = False
                translator_comments = []
                messages = []
                call_stack = -1

            elif token_type == 'Token.Literal.Scalar.Flow':
                if DEBUG:
                    print call_stack, ' in flow', value
                new_value = value
                if concatenate_next:
                    # print '   concat next'
                    last_argument = (last_argument or '') + new_value
                    # print '      ' + last_argument
                else:
                    last_argument = new_value

            elif token_type == 'Token.Text.Blank':
                if DEBUG:
                    print call_stack, ' in flow', value
                concatenate_next = True
            # elif token_type == 'operator':
            #     if value == ',':
            #         if last_argument is not None:
            #             messages.append(last_argument)
            #             last_argument = None
            #         else:
            #             messages.append(None)
            #         concatenate_next = False
            #     elif value == '+':
            #         concatenate_next = True

        elif call_stack > 0 and token_type == 'Token.Literal.Scalar.Flow.Quote':
            if DEBUG:
                print call_stack, '  call_stack>0, got quote   ', value
            call_stack -= 1

        elif funcname and call_stack == -1:
            if DEBUG:
                print call_stack, '  has funcname quote end  ', value
            yield (message_lineno, funcname, last_argument,
                   [comment[1] for comment in translator_comments])
            funcname = None
            last_argument = ''
            # Done here, so yield  the message

        elif call_stack == -1 and token_type == 'Token.Name.Type' and \
                value in keywords.keys() \
              and (last_token is None or last_token[0] != 'Token.Name.Type') and \
              (last_token[1] != 'function'):
            if DEBUG:
                print call_stack, '  got funcname  ', value
            funcname = value

        last_token = (token_type, value)

if __name__ == "__main__":
    print list(extract_yaml(open('configs/sanit.config.yaml', 'r'), keywords={'!gettext': None}, comment_tags={}, options={}))

