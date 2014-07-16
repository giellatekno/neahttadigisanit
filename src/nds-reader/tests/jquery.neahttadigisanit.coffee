assert = chai.assert
expect = chai.expect


describe 'Neahttadigisánit Reader', ->
  describe "$.fn.selectToLookup", ->
    it "Exists", ->
      expect(jQuery.fn.selectToLookup).is.a('function')

  Templates = nds_exports.Templates
  describe "Templates", ->
    describe "NotifyWindow", ->
      it "Renders", ->
        console.log Templates.NotifyWindow("asdf")

