// SPDX-License-Identifier: AGPL-3.0-or-later
// Bounded HydraPy adaptation; see SOURCES.md
vec4 Process(vec4 c){
 vec2 uv=gl_TexCoord[0].st;float t=timer*.015;
 // Bounded recurring seed sequence, inspired by Seq/EntropyLock rather than a recurrent render target.
 float k=floor(t);float a=fract(sin(mod(k,16.)*23.17+4.1)*731.9);
 float b=fract(sin(mod(k+1.,16.)*23.17+4.1)*731.9);
 float seed=mix(a,b,smoothstep(0.,1.,fract(t)));
 vec2 q=uv+vec2(sin(uv.y*11.+t),cos(uv.x*13.-t))*.006;
 float trail=.5+.5*cos((q.x+q.y)*17.+seed*6.28);
 return getTexel(q)*c*vec4(mix(vec3(.88,.91,.84),vec3(1.05,1.04,.98),trail),1.);
}