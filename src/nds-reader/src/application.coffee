### This is the initial coffeescript file that sets up the module
    and provides some prototype definitions, as well as the
    internationalization function which must be present for everything else.
###

# if not window.rangy?
#   rangy = require 'rangy'
#   rangy_textrange = require 'rangy-textrange'

Array::zipPermutations = (right_list) ->
  left_list = this

  leftPermutations = (sublist) ->
    perms = []
    for x of _.range(1, sublist.length+1)
      _i = -Math.abs(x)
      if x > 0
        perms.push sublist.slice(_i)
    perms.push(sublist)
    return perms

  rightPermutations = (sublist) ->
    perms = []
    for x of _.range(1, sublist.length+1)
      if x > 0
        perms.push sublist.slice(0, x)
    perms.push(sublist)
    return perms

  lefts = leftPermutations(left_list)
  rights = rightPermutations(right_list)

  combined = []
  for l in lefts
    combined.push l

  for l in lefts
    for r in rights
      combine = l.concat(r)
      combined.push combine

  for r in rights
    combined.push r

  # for c in combined
  #   console.log c.join(' ')

  return combined

String::startsWith = (str) ->
  return this.slice(0, str.length) == str

String::endsWith = (str) ->
  return this.slice(-str.length) == str

JQPlugin = require('src/jquery.neahttadigisanit')
FakeGetText = require('src/localization')

rangy = require('rangy')
rangyTextRange = require('rangy-textrange')

module.exports = class Application

  checkmodules: () ->
    empty = JSON.stringify {}
    for l in ndsrequire.list()
      a = JSON.stringify require(l)
      if a == empty and (not a.startsWith('lib/bootstrap'))
        console.log "#{l} failed to initialize"

  constructor: () ->
    console.log "Initializing NDS."
    # @checkmodules()
    if window.rangy?
      rangz = window.rangy
    else if rangy?
      rangz = rangy
    if rangz.init?
      console.log "found rangy"
      window.rangy.init()
    else
      console.log "couldn't find rangy"

