// SPDX-License-Identifier: AGPL-3.0-or-later
// Original bounded GLSL adaptation; HydraPy operator attribution: SOURCES.md
vec4 Process(vec4 c) {
 vec2 p=gl_TexCoord[0].st;float t=timer*.12;
 vec2 q=p+.008*vec2(sin(p.y*25.+t),cos(p.x*31.-t));
 float f=pow(max(0.,sin(q.x*37.+t)*sin(q.y*33.-t)),8.);
 return getTexel(q)*c*vec4(vec3(.9)+vec3(.13,.21,.19)*f,1.);
}