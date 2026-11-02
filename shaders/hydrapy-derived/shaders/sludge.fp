// SPDX-License-Identifier: AGPL-3.0-or-later
// Original bounded GLSL adaptation; HydraPy operator attribution: SOURCES.md
vec4 Process(vec4 c) {
 vec2 p=gl_TexCoord[0].st; float t=timer*.035;
 vec2 q=p+0.035*vec2(sin(p.y*19.+t),cos(p.x*17.-t));
 float v=sin(q.x*29.+sin(q.y*21.+t))*cos(q.y*23.-t);
 return getTexel(q)*c*vec4(mix(vec3(.72,.80,.60),vec3(1.08,1.06,.86),.5+.5*v),1.);
}