// SPDX-License-Identifier: AGPL-3.0-or-later
// Original bounded GLSL adaptation; HydraPy operator attribution: SOURCES.md
vec4 Process(vec4 c) {
 vec2 p=gl_TexCoord[0].st*5.;float f=0.;
 for(int k=0;k<5;k++){float a=3.14159265*float(k)/5.;f+=cos(6.2831853*dot(p,vec2(cos(a),sin(a)))+timer*.012);}
 float line=1.-smoothstep(.025,.11,abs(f*.2));
 return getTexel(gl_TexCoord[0].st)*c*vec4(mix(vec3(.86),vec3(1.10,.98,.81),line),1.);
}