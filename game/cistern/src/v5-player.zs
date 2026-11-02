class C5Player:NRFeelPlayer {
 int StepAge,StepPeriod,StepNumber,Burn,RepairAge,Medical,Salvage,Immune;double Injury,Heat;bool Hurry,SavedBlow;C5Stone Grip;
 Default {Height 60;Radius 12;Player.ViewHeight 50;Player.DisplayName "Cistern cyborg";}
 override void MovePlayer(){
  if(!player)return;if(level.levelnum!=4){Super.MovePlayer();return;}
  // The only camera-yaw write is the raw native input; pitch stays in native look code.
  Angle+=player.cmd.yaw*(360./65536.);
  Hurry=(player.cmd.buttons&BT_SPEED)!=0;bool od=(player.cmd.buttons&BT_USER4)!=0;
  if(Immune>0)Immune--;if(MoveCooldown>0)MoveCooldown--;
  MoveBurst=0;if(od&&MoveCooldown==0&&Burn<63){Burn++;MoveBurst=63-Burn;Heat=min(1.,Heat+.016);if(Burn==63)MoveCooldown=210;}else{if(!od)Burn=0;Heat=max(0.,Heat-.004);}
  double f=player.cmd.forwardmove,side=player.cmd.sidemove;double len=sqrt(f*f+side*side),input=clamp(len/6400.,0.,1.);if(len>0){f/=len;side/=len;}
  let trim=CVar.GetCVar('nr_walk_scale');double scale=clamp(round(trim.GetFloat()*20)/20,.8,1.5);if(abs(trim.GetFloat()-scale)>.001)trim.SetFloat(scale);
  int profile=CVar.GetCVar('nr_walk_profile').GetInt();double ms=Hurry?4.03:profile==1?4.03:2.65;if(MoveBurst>0)ms=5.4408;

  MoveQuiet=player.crouchfactor<.9;double body=1-Injury*.25;
  ms*=body*NRWeight.Slow(self);if(input>.99&&!MoveQuiet&&player.crouchfactor>.9)ms=max(1.85,ms);
  ms*=scale;if(MoveQuiet)ms*=.55;if(player.crouchfactor<.9)ms*=.45;
  if(Grip)ms*=Grip.Stage==1?.45:Grip.Stage==2?0:1;
  if((player.cmd.buttons&BT_USER3)!=0&&Medical>0&&(health<100||Injury>0)){
   RepairAge++;ms*=.25;if(RepairAge>=70){Medical--;health=min(100,health+45);player.health=health;Injury=0;SavedBlow=false;RepairAge=0;A_StartSound("c5/repair",CHAN_ITEM);Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY, "C5 FIELD_REPAIR health=%d",health);}
  }else RepairAge=0;
  Vector2 dir=(cos(Angle)*f+sin(Angle)*side,sin(Angle)*f-cos(Angle)*side);double friction,factor;[friction,factor]=GetFriction();
  Vector2 desired=dir*(ms*32/35)*input*clamp(friction,.5,1.);Vector2 diff=desired-Vel.XY;double dl=diff.Length();double accel=input>.01?.42:.62;
  bool ground=Pos.Z<=floorz+.5||bONMOBJ;if(!ground)accel*=.1;if(dl>accel)diff*=accel/dl;
  Vector2 velocity=Vel.XY+diff;if(ground)velocity/=clamp(friction,.5,1.);Vel.X=velocity.X;Vel.Y=velocity.Y;player.onground=ground;
  player.cmd.buttons&=~BT_JUMP;MaxStepHeight=8;
  if(input>.01)PlayRunning();MoveWeight+=(input-MoveWeight)*.15;
  if((player.cmd.buttons&BT_ATTACK)!=0)MoveGunNoise=12;else if(MoveGunNoise>0)MoveGunNoise--;
  MoveNoise=input>.01?(Hurry?1.5:MoveQuiet?.12:.45):0;if(MoveBurst>0)MoveNoise=2.;if(MoveGunNoise>0)MoveNoise=3.;
  if(input>.01&&ground&&Vel.XY.Length()>.3){StepAge++;if(StepAge>=max(16,StepPeriod)){
    StepAge=0;StepNumber++;StepPeriod=MoveBurst>0?16:16;
    if(Injury>0)StepPeriod+=StepNumber%2==0?2:0;
    NRSFX.Step(self,NRFeelMaterial.At(self),Hurry||MoveBurst>0?.9:MoveQuiet?.16:.38);A_StartSound("feel/servo",5,0,Hurry?.2:.1);
   }}else{StepAge=0;MoveWeight*=.8;}
  MovePhase=360.*StepAge/max(16,StepPeriod);
  double turn=deltaangle(MoveOldYaw,Angle);MoveOldYaw=Angle;double tilt=Pitch-MoveOldPitch;MoveOldPitch=Pitch;
  MoveSwayX+=(clamp(-turn,-5.,5.)-MoveSwayX)*.12;MoveSwayY+=(clamp(tilt,-3.,3.)-MoveSwayY)*.12;
  double lean=((player.cmd.buttons&BT_USER2)!=0?1.:0.)-((player.cmd.buttons&BT_USER1)!=0?1.:0.);MoveLean+=(lean*8-MoveLean)*.25;
  Vector2 lateral=(sin(Angle),-cos(Angle));if(CheckMove(Pos.XY+lateral*MoveLean))SetViewPos((lateral.X*MoveLean,lateral.Y*MoveLean,0),VPSF_ABSOLUTEOFFSET);else SetViewPos((0,0,0),VPSF_ABSOLUTEOFFSET);
  Roll=clamp(MoveLean/8*1.5,-1.5,1.5);NRWeight.Tick(self);
  if(input>.99)Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY,"C7 WALK tic=%d profile=%d scale=%.2f x=%.5f y=%.5f z=%.3f step=%d period=%d hurry=%d overdrive=%d",level.time,profile,scale,Pos.X,Pos.Y,Pos.Z,StepNumber,StepPeriod,Hurry,MoveBurst>0);
 }
 override void CalcHeight(){Super.CalcHeight();if(!player||level.levelnum!=4)return;
  double dip=.7*(1+cos(MovePhase))*.5*MoveWeight;double eye=player.viewheight;
  player.viewz=clamp(Pos.Z+eye-dip,Pos.Z+4,ceilingz-4);
 }
 override Vector2 BobWeapon(double ticfrac){Vector2 w=NRWeight.Bob(self);double tremor=Injury*sin(level.time*18)*.35;return w+(MoveSwayX*.2+tremor,MoveSwayY*.2+RepairAge/70.*2);}
 override int DamageMobj(Actor inflictor,Actor source,int damage,Name mod,int flags,double angle){
  if(mod=='Heavy'&&damage>=60){if(health>=80&&!SavedBlow&&damage>=health)damage=health-12;SavedBlow=true;Injury=max(Injury,.65);Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY, "C5 HEAVY_BLOW before=%d damage=%d",health,damage);}
  return Super.DamageMobj(inflictor,source,damage,mod,flags,angle);
 }
}
class C5HUD:EventHandler {
 ui double ReportedScale;ui int ReportedProfile;
 override void UiTick(){
  let c=CVar.GetCVar('nr_walk_scale');let profileCVar=CVar.GetCVar('nr_walk_profile');if(!c||!profileCVar)return;
  double scale=clamp(round(c.GetFloat()*20)/20,.8,1.5);int profile=profileCVar.GetInt();
  if(abs(ReportedScale-scale)>.001||ReportedProfile!=profile){ReportedScale=scale;ReportedProfile=profile;Console.Printf("Walking: %s %.2f m/s (x%.2f)",profile==0?"careful":"brisk",(profile==0?2.65:4.03)*scale,scale);}
 }

 override void RenderOverlay(RenderEvent e){let p=C5Player(players[consoleplayer].mo);if(!p||level.levelnum!=4)return;
  String s=CVar.GetCVar('nr_walk_profile').GetInt()==0?"CAREFUL":"BRISK";s=s.." / SHIFT: HURRY / ALT: OVERDRIVE / F7: PROFILE";
  if(p.MoveBurst>0)s="OVERDRIVE / HEAT";else if(p.MoveCooldown>0)s="SERVO COOLING";
  Screen.DrawText(smallfont,Font.CR_GOLD,12,44,s);
  if(p.Medical>0||p.Salvage>0)Screen.DrawText(smallfont,Font.CR_WHITE,12,60,String.Format("MEDICAL TINS %d / HOLD G TO REPAIR / SCRAP %d",p.Medical,p.Salvage));
  if(p.RepairAge>0)Screen.DrawText(smallfont,Font.CR_GOLD,12,76,String.Format("FIELD REPAIR %d%%",p.RepairAge*100/70));
 }
 override void NetworkProcess(ConsoleEvent e){
 if(e.Name=='c5_profile'){let c=CVar.GetCVar('nr_walk_profile');c.SetInt(c.GetInt()==0?1:0);}
 if(e.Name=='c7_slower'||e.Name=='c7_faster'){let c=CVar.GetCVar('nr_walk_scale');c.SetFloat(clamp(round(c.GetFloat()*20)/20+(e.Name=='c7_faster'?.05:-.05),.8,1.5));}
 }
}
