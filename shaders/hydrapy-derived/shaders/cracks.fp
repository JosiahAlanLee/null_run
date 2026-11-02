// SPDX-License-Identifier: AGPL-3.0-or-later
// Bounded HydraPy adaptation; see SOURCES.md
vec2 sites(vec2 p){return fract(sin(vec2(dot(p,vec2(127.1,311.7)),dot(p,vec2(269.5,183.3))))*43758.5453);}
vec4 Process(vec4 c){
 vec2 uv=gl_TexCoord[0].st;vec2 p=uv*6.;float t=timer*.012;
 p+=.15*vec2(sin(p.y*1.7+t),cos(p.x*1.3-t));
 vec2 cell=floor(p),f=fract(p);float first=8.,second=8.;
 for(int y=-1;y<=1;y++)for(int x=-1;x<=1;x++){
  vec2 o=vec2(float(x),float(y));float d=length(o+sites(cell+o)-f);
  if(d<first){second=first;first=d;}else if(d<second)second=d;
 }
 float width=.025+.007*sin(t);float edge=1.-smoothstep(0.,width,second-first);
 return getTexel(uv)*c*vec4(vec3(1.-edge*.18),1.);
}