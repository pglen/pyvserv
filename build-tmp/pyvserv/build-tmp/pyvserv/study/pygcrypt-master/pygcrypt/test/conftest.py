#!/usr/bin/env python

import pytest

from pygcrypt.context import Context
from pygcrypt.gctypes.key import Key
from pygcrypt.gctypes.sexpression import SExpression

@pytest.fixture
def context():
    return Context()

@pytest.fixture
def private():
    return Key(SExpression(b"""
(private-key 
  (rsa
    (n #00D3D01AD42539298A201D311F3145D87A6BA22851702D91633731AAD6491771CB2BEBB5695DD3628AB21E76EBEF0D718E281AF6E963B3CF9D25C0384052CCC4B97AF75A2B11821F3D2EAAF3C468F65178EEA5ABF5E84EEBB40AC00C78BF6C8D72C7071871FBDC8E26767DCFF88F8362657FF3046235C50F67E1AC2CEFF3699D13F13A9649FB7297BC0F6688C696766E0C6E0143211EFCD546988177A39F71A243D6B352220D9C5FEFF9548CF8DE6111023B35C32EAFAC884EB1B4B4EEB17F7D2A4CA01D1B8413BFDB5FCEA09865D756F4C2D24B3B811D918D4B55D3CE34AF8CA648D69ACBE717343278798A3D01E6E5A174A491A48272E72ACBC3159427079BF1493E303C0F1BDCBBA032505071079761C667CF59ADE988CFEC50191180B9F6FC954353A71E86FFB8458B00F21B47F6F13A302587BE0CF51CC92AA610122F1D17308450F033075567D8C5CF2D0F9DA4B9CBA4F85DB0E6EDFE6BE5C6BE8E31B6E07CA205FA8883F19D1DE0D72B3297F3FD53CEFDBBBFBC9F42142DF077126251E57CF06D6CD47762AF930F1F3AC1E07FD01F0A6994C2F177BFD35BB7E8339506D186B92B85AB0692EB82CDA09A46F4CC3158A2BCC971E317F1DDF9B3298A46BDE9E6F379F903F0754372C03463AEC2D96554FAB0F8E756FFC2FF3EB6094C1D48ABDCB653EC42CB3832A2A363E5D96AF3CA7C2412256F2A8DA92AE615CEE00518EB#)
    (e #010001#)
    (d #113EE8704D779202450B1B6CC6BE4119F699855EDC1B59B3125360ED8195FF15E3C59547B6F3F71A03D6A7281E96A1A04973A896E81F43D02FBAAED9CDE40E406BDAA7E4C9D0266AFCD9BE6F477C86B5A9F8A33FAA62829E6E21A4E24FF3AEB0A1B3DA31ADA80F8AE22AEC3BF8B361D791CB5F97FF78C4005947838125F87B699C4280EA15270763B07D50B59A9A99EB3929B12589385CC51AB5AFE00AA35DEAD818519FA42C0F43A2B157A90BB22B885AF9CDA2877B2CBDFB8A13113C327D266C86BCD7F8B102F6019EF9446F4651362C86A2C97D81C2D0164A2EACA36D87AE225016DA733E5869A39581C3E5DBBEE69E70A7CB1533F5CE6E38BC110BFC7A9DCCC273D9BA3CFC883A1E60A029174B4C053BCC308DE3CBB87B3DA0A7D59F5E9977828C818B2080C70076906ED5C1419CF2B2D9FA6711BAA1B34BFC1FACD3D8BBBD98DE1DADD3AE032C3714A46FB475DDC7887CA00A23E343F8F3744ECD0C1882317A9C44C17063C62D31598190942F8411E3F31A428D51996028EA97B9BD8141B9279BCB07952F406708971597CF9C72C95B07F4694B27A2BC8A98EB813EB2BBBD0DB1CF2CEE6256832C4B1A13E5F1F8907F568DEB491B21D7384BAD2E3C86B2789379129D779EE0A06944EADCFEA4E1CA8C0A9F83820D6CA4E48D7382E83A0E129D02A8ACBFCEC2F4E1124F39A07A5F5E7BD7726E2B06F7C9C0EC9C7371AEC1#)
    (p #00E31EBA29F18D0317D9CD973DF9AC413AC9FBAA801D35C4585F1EDBF043B1C855CA6224CE9DF88AD467AD50950ABE121EE9E43A240A005972D3DA54414B4974FC712B4F6BA5698564C1934D066837BEB23C49ADE82C92AE5829F68024F0F8314CCBEF198D773FDE184CA2ABBBA165447320581EBF9BE14CEFD7C98E708F83C15E2CDEA0A8D591AF48E47B90B0C1555DB823417C07741D0F146531333E6520D909CA8C8E2543EF24125481E3984B66C1598D87B91AFFFF9095B231C89096703B208D103DFFD47EDC97E3DEE8E81C90B5B2C8AD2863EB8319F3484759A08A8901D541542101263D1CD08AC4E0F76F44E6140AE595CFBA20DF706E201E6AE251248D#)
    (q #00EEBF189AD7C4422B52EF25604C033BE4F2117F38441D9F084C0922C4D2C15BE69868797DF0E9FFDA364234226DCCB4EE823383E49CD29249B8C87AB318DCF23301E8C17DD6DBCE25E9083F955DA9F2F8B75B1763274255888085DC2D50B539AA3D5376A09B92E3FED26AC0FB2C5D48AAC1DB307029A2519DC2FFB17162C32B9FC2C3A6421B49EE3D501CAAA4EBF3B55C681F9B0F5BE6673C4F349E7830FC9FA7816204C56797A8F3C873BCB3BBD773B1AD8E960B3CF8548E5647F826DEA587D2FB2F887163268B9BDB2ABAF8FC0DF8B0A80A80BC38C72FF2E9F48FD61FD1106B4CF056B93EB0DD751BE5D7BD192DEBF1E43B83B5C60C1EED17B39F3D9B89A157#)
    (u #0085C72E87702CF7D0C84A9C4753F1D3FA07798D3E0AF8C617F186E7A756980E46FBC64656C347BB83F31AAA14236DABA5D034BE373CA5D851428D80618D7AC726CC11D8F420DB2ABB86310D01EE42B4AE1A49939DB76F4D1CD6BB3441308F204882BCE5A957449C8663B9B182831A8472FFE2ECD913E8D44DE9FC2BC5933D6169E03C58CE17A7F65AD68193E67E80A29209D746617CB2A64CF5506E9058D9330EEAA36A87D76FB3D28415C28019903DCE81A34E897D1B4AB7FD0F8E122EB32E945359F7D2397739FFA4953E83AF8E4B60B2605717BC85F6A2B133B12A23A28E443D14FA5DE5D9482A63F562202C487B97F48A40DD3A41C7D2AD1DF472A1EA4F02#)
 )
)"""))

@pytest.fixture
def public():
    return Key(SExpression(b"""
(public-key 
  (rsa 
    (n #00D3D01AD42539298A201D311F3145D87A6BA22851702D91633731AAD6491771CB2BEBB5695DD3628AB21E76EBEF0D718E281AF6E963B3CF9D25C0384052CCC4B97AF75A2B11821F3D2EAAF3C468F65178EEA5ABF5E84EEBB40AC00C78BF6C8D72C7071871FBDC8E26767DCFF88F8362657FF3046235C50F67E1AC2CEFF3699D13F13A9649FB7297BC0F6688C696766E0C6E0143211EFCD546988177A39F71A243D6B352220D9C5FEFF9548CF8DE6111023B35C32EAFAC884EB1B4B4EEB17F7D2A4CA01D1B8413BFDB5FCEA09865D756F4C2D24B3B811D918D4B55D3CE34AF8CA648D69ACBE717343278798A3D01E6E5A174A491A48272E72ACBC3159427079BF1493E303C0F1BDCBBA032505071079761C667CF59ADE988CFEC50191180B9F6FC954353A71E86FFB8458B00F21B47F6F13A302587BE0CF51CC92AA610122F1D17308450F033075567D8C5CF2D0F9DA4B9CBA4F85DB0E6EDFE6BE5C6BE8E31B6E07CA205FA8883F19D1DE0D72B3297F3FD53CEFDBBBFBC9F42142DF077126251E57CF06D6CD47762AF930F1F3AC1E07FD01F0A6994C2F177BFD35BB7E8339506D186B92B85AB0692EB82CDA09A46F4CC3158A2BCC971E317F1DDF9B3298A46BDE9E6F379F903F0754372C03463AEC2D96554FAB0F8E756FFC2FF3EB6094C1D48ABDCB653EC42CB3832A2A363E5D96AF3CA7C2412256F2A8DA92AE615CEE00518EB#)
    (e #010001#)
  )
)"""))
