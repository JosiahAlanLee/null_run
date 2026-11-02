// SPDX-License-Identifier: AGPL-3.0-or-later
// Original bounded GLSL adaptation; HydraPy operator attribution: SOURCES.md
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
void main(){
 vec2 uv=TexCoord; vec2 size=vec2(textureSize(InputTexture,0));
 float t=Clock;vec2 d=uv-.5;float r=length(d);
 // Bounded subpixel gate drift and decaying radial displacement.
 if((Parts & 1)!=0)uv+=vec2(sin(t*.71),sin(t*.53+1.2))*.28/size*Strength;
 if((Parts & 2)!=0)uv+=normalize(d+vec2(.00001))*sin(r*64.-t*13.)*Ripple*.002;
 if((Parts & 4)!=0)uv.x+=Tear*.003*sin(uv.y*19.+t*4.);
 vec2 fringe=vec2(.65/size.x,0)*Strength;
 vec3 col=texture(InputTexture,uv).rgb;
 if((Parts & 8)!=0){col.r=texture(InputTexture,uv+fringe).r;col.b=texture(InputTexture,uv-fringe).b;}
 if((Parts & 16)!=0){vec3 halo=texture(InputTexture,uv+vec2(2.,0)/size).rgb+texture(InputTexture,uv-vec2(2.,0)/size).rgb;
 col+=max(halo*.5-vec3(.72),vec3(0.))*.08*Strength;}
 float grain=0.;if((Parts & 32)!=0)grain=(hash(floor(uv*size)+floor(t*12.))-.5)*.018*Strength;
 float vign=(Parts & 64)!=0?1.-.09*Strength*smoothstep(.25,.68,r):1.;
 col=(col+grain)*vign;
 vec2 m=abs(TexCoord-.5);float crop=step(.455,m.x)*step(.40,m.y)*step(m.y,.403)+step(.455,m.y)*step(.40,m.x)*step(m.x,.403);
 if((Parts & 64)!=0)col*=1.-crop*.18*Strength;FragColor=vec4(col,1.);
}