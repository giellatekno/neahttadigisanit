assert = chai.assert
expect = chai.expect

DictionaryAPI = module.DictionaryAPI

describe 'DictionaryAPI', ->
  describe "DictionaryAPI.config", ->
    # TODO: callback
    it "Returns the configuration result"

  describe "DictionaryAPI.lookup", ->
    # TODO: callback
    it "Returns the lookup result"

describe 'Neahttadigisánit Reader', ->
  describe "$.fn.selectToLookup", ->
    it "Exists", ->
      expect(jQuery.fn.selectToLookup).is.a('function')

  describe "Templates", ->
    describe "NotifyWindow", ->
      it "Renders", ->
        console.log module.Templates.OptionsTab(window.nds_opts)

