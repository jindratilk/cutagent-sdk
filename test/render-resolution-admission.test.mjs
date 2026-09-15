import assert from 'node:assert/strict';
import test from 'node:test';
import {renderDiscoverySupports} from '../runtime/bridge/services/sdk-render-action-service.js';
const input={settings:{format:'mp4',codec:'h264',width:640,height:360}};
const discovery=(resolutionSupport,resolutions=[])=>({formats:[{format:{kind:'known',value:'mp4'},codecSupport:{availability:'supported'},codecs:[{codec:{kind:'known',value:'h264'},resolutionSupport,resolutions}]}]});
test('Free missing resolution enumeration does not falsely reject an exposed codec',()=>{
 assert.equal(renderDiscoverySupports(discovery({availability:'unavailable',reason:'api_unavailable'}),input),true);
});
test('known unsupported dimensions and explicit edition restrictions remain rejected',()=>{
 assert.equal(renderDiscoverySupports(discovery({availability:'supported'},[{width:1920,height:1080}]),input),false);
 assert.equal(renderDiscoverySupports(discovery({availability:'unavailable',reason:'edition_unavailable'}),input),false);
 assert.equal(renderDiscoverySupports(discovery({availability:'unknown_version',reason:'unrecognized_response'}),input),false);
 assert.equal(renderDiscoverySupports({formats:[]},input),false);
 assert.equal(renderDiscoverySupports(discovery({availability:'supported'},[{width:640,height:360}]),input),true);
});
