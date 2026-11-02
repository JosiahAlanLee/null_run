// SPDX-License-Identifier: AGPL-3.0-or-later
class NREngineFX: StaticEventHandler {
 double Tear,Ripple,Strength; int LastHealth;bool Enabled;int Mode;int Parts;NRSigilCaster Caster;FXApplicant Subject;FXLight Lamp;
 void SigilCompleted(){Ripple=1;Console.Printf("NRRECEIPT {\"fx\":\"sigil_completed\",\"tic\":%d}",level.time);}
 override void WorldLoaded(WorldEvent e){Enabled=true;LastHealth=100;Parts=127;}
 override void NetworkProcess(ConsoleEvent e){
  if(e.Name=="fx_subject"){
   let p=players[0].mo;if(!p)return;if(Subject)Subject.Destroy();if(Lamp)Lamp.Destroy();
   Subject=FXApplicant(Actor.Spawn(e.Args[0]==0?"FXApplicantFlat":e.Args[0]==1?"FXApplicant":"FXApplicantRim",(0,400,32)));Subject.Angle=270;
   Lamp=FXLight(Actor.Spawn("FXLight",(-70,360,120)));
  }
  
if(e.Name=="fx_pack"){let p=players[0].mo;Actor.Spawn("NRDepthPiece56",(0,310,0));Actor.Spawn("FXScreen",(-110,300,40));Lamp=FXLight(Actor.Spawn("FXLight",(-60,280,90)));p.SetOrigin((0,170,0),false);p.Pitch=5;}
if(e.Name=="fx_parts")Parts=e.Args[0];
  if(e.Name=="fx_cast"){
   if(!Caster)Caster=NRSigilCaster(Actor.Spawn("NRSigilCaster",(-96,520,64)));Caster.StartCast();
  }
  if(e.Name=="fx_break" && Caster)Caster.DamageMobj(null,null,1,'FXProbe');
  if(e.Name=="fx_hurt"){let p=players[0].mo;if(p)p.DamageMobj(null,null,5,'FXProbe');}
  if(e.Name=="fx_toggle")Enabled=!Enabled;
  if(e.Name=="fx_damage")Tear=1;
  if(e.Name=="fx_sigil")Ripple=1;
  if(e.Name=="fx_camera"){
   let p=players[0].mo;let h=NRDirector.Get();if(!p||!h)return;
   for(int i=0;i<h.Mobs.Size();i++)if(h.Mobs[i])h.Mobs[i].Destroy();h.Mobs.Clear();h.HaveLast=false;
   p.SetOrigin((0,160,level.levelnum==6?32:0),false);p.Vel=(0,0,0);p.Angle=90;p.Pitch=0;p.Health=10000;
  }
 }
 override void WorldTick(){
  let p=players[consoleplayer].mo;if(!p)return;
  if(p.Health<LastHealth)Tear=min(1.,Tear+.6);LastHealth=p.Health;
  Tear=max(0.,Tear-1./18.);Ripple=max(0.,Ripple-1./28.);
  double near=0.;if(Subject)near=clamp(1.-p.Distance3D(Subject)/600.,0.,1.);let h=NRDirector.Get();
  if(h){for(int i=0;i<h.Mobs.Size();i++)if(h.Mobs[i])near=max(near,clamp(1.-p.Distance3D(h.Mobs[i])/600.,0.,1.));}
  Strength+= (min(.85,.22+near*.60)-Strength)*.06;
 }
 override void RenderOverlay(RenderEvent e){
  PPShader.SetEnabled("NREmulsion",Enabled);
  PPShader.SetUniform1i("NREmulsion","Parts",Parts);
  PPShader.SetUniform1f("NREmulsion","Clock",level.time/35.);
  PPShader.SetUniform1f("NREmulsion","Strength",Strength);
  PPShader.SetUniform1f("NREmulsion","Tear",Tear);
  PPShader.SetUniform1f("NREmulsion","Ripple",Ripple);
 }
}

class FXApplicant: Actor {
 Default {Radius 24;Height 140;Scale .2145833333;+NOGRAVITY;}
 States {Spawn: FXA0 A -1;Stop;}
}
class FXApplicantFlat: FXApplicant {States {Spawn: FXBA A -1;Stop;}}
class FXLight: Actor {Default {+NOGRAVITY;+NOINTERACTION;} States {Spawn: TNT1 A -1;Stop;}}

class FXScreen:Actor {Default {+NOGRAVITY;Scale .16;} States {Spawn: FXSC A -1;Stop;}}

class FXApplicantRim:FXApplicant {States {Spawn: FXRC A -1;Stop;}}
class FXBakeMarker:Actor { Default { +NOINTERACTION +NOGRAVITY } States {Spawn: TNT1 A -1;Stop;} }
