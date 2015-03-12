### This is the initial coffeescript file that sets up the module
    and provides some prototype definitions, as well as the
    internationalization function which must be present for everything else.
###
rangy = require 'rangy'
rangy_textrange = require 'rangy-textrange'

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

module.exports = class Application

  constructor: () ->
    @rangy = rangy
    console.log "zomg"
