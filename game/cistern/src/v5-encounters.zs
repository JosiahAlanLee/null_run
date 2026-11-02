// Adapted from panic01 and anatomy01. No lab teleport, forced phase, invulnerability or scripted route.
class C5Enemy:Actor {
 bool Active;int Age,Stall,Warn,AttackAge,Phase;Vector3 Home,Committed;double ChaseSpeed;
 Default {Health 80;Radius 18;Height 64;+SOLID +SHOOTABLE +NOBLOOD Mass 120;MaxStepHeight 8;}
 States {Spawn:E2IP A -1;Stop;Death:TNT1 A 1;Stop;}
 override void PostBeginPlay(){Super.PostBeginPlay();Home=Pos;ChaseSpeed=1.25;}
 bool Notice(C5Player p,double sight=230){if(!p)return false;return (Distance2D(p)<sight&&CheckSight(p))||(p.MoveNoise>1&&Distance2D(p)<p.MoveNoise*180);}
 void Steer(Vector3 goal,double speed){double aim=atan2(goal.Y-Pos.Y,goal.X-Pos.X);bool found=false;Vector2 v;
  for(int j=0;j<9;j++){double off=j==0?0:((j+1)/2)*25*(j%2==1?1:-1);double a=aim+off;v=(cos(a)*speed,sin(a)*speed);if(CheckMove(Pos.XY+v*3)){Angle=a;Vel.X=v.X;Vel.Y=v.Y;found=true;break;}}
  if(!found){Vel.X=0;Vel.Y=0;Stall++;if(Stall==35)Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY, "C5 AI_STUCK %s tic=%d",GetClassName(),level.time);}else Stall=0;
 }
 virtual void PictureHit(Actor shooter,Vector3 origin,Vector3 dir,int kind,int damage){
  double t=(Pos.XY-origin.XY).Length();Vector3 point=origin+dir*t;double z=point.Z-Pos.Z;
  if(z<Height*.35){ChaseSpeed=.45;damage=int(damage*1.3);Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY, "C5 LOW_HIT %s crippled",GetClassName());}
  DamageMobj(shooter,shooter,damage,'C5Shot');
 }
 override int DamageMobj(Actor inflictor,Actor source,int damage,Name mod,int flags,double angle){
  if(mod=='Hitscan'&&source&&source.player){int k=NRMechanics.Kind(source.player.ReadyWeapon);int material=k==1?0:(k==2||k==4)?1:(k==3||k==5)?2:3;Vector3 eye=(source.Pos.X,source.Pos.Y,source.player.viewz);Vector3 dir=(cos(source.Pitch)*cos(source.Angle),cos(source.Pitch)*sin(source.Angle),-sin(source.Pitch));PictureHit(source,eye,dir,material,damage);return damage;}
  return Super.DamageMobj(inflictor,source,damage,mod,flags,angle);
 }
 override void Die(Actor source,Actor inflictor,int flags,Name mod){Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY, "C5 ENEMY_DEAD %s tic=%d",GetClassName(),level.time);bSOLID=false;Super.Die(source,inflictor,flags,mod);}
}
class C5Hollow:C5Enemy {
 Default {Health 80;Radius 24;Height 88;Scale .75;}
 int ArtDeath,ArtHit,Blows;
 States {Spawn:K20I A -1;Stop;Crawl:K20C A -1;Stop;Pounce:K20T A -1;Stop;Death:K20D ABCD 5;K20X A -1;Stop;}
void ArtPicture(){let p=players[0].mo;if(!p)return;
 int b=clamp(int(round(atan2(p.player.viewz-Pos.Z-44,Distance2D(p))/22.5))+2,0,4);
 int y=(int(round(deltaangle(Angle,AngleTo(p))/45))+8)%8;
 String c="I";int f=0;
 if(health<=0){ArtDeath++;c=ArtDeath>=20?"X":"D";f=ArtDeath>=20?0:min(3,ArtDeath/5);}
 else if(Phase==0&&Active&&Age>=77){c="F";f=min(3,(Age-77)/7);}
 else if(Phase==1){c="C";f=(Age/4)%4;}
 else if(Phase==2){c="T";f=min(3,Age/9);}
 else if(Phase==3){c="P";f=min(3,Age/4);}
 else if(Phase==4){c="R";f=(Age/8)%4;}
 else if(Phase==5){c="F";f=3-min(3,Age/8);}
 else if(Phase==6){c="R";f=min(3,Age/5);}
 if(health>0&&ArtHit>0){c="H";f=min(3,(12-ArtHit)/3);ArtHit--;}
 sprite=GetSpriteIndex(String.Format("K%d%d%s",b,y,c));frame=f;
 }
 override void Tick(){Super.Tick();ArtPicture();if(health<=0){if(ArtDeath>=35)Destroy();return;}Vel.X=0;Vel.Y=0;let p=C5Player(players[0].mo);if(!p||p.health<=0)return;
  if(!Active)return;Age++;
  if(Phase==0){if(Age<105)return;Phase=1;Age=0;Height=32;SetStateLabel('Crawl');A_StartSound("c5/wood",CHAN_VOICE);Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY, "C5 HOLLOW_CRAWL tic=%d",level.time);}
  if(Phase==1){Steer(p.Pos,ChaseSpeed<1?.45:2.0);if(Distance2D(p)<144&&CheckSight(p)){Blows++;Phase=Blows%2==0?5:2;Age=0;Committed=p.Pos;Angle=AngleTo(p);SetStateLabel('Pounce');A_StartSound("c5/wood",CHAN_VOICE);Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY, "C5 HOLLOW_POUNCE_WARN tic=%d",level.time);}}
  else if(Phase==2){if(Age>=35){Phase=3;Age=0;}}
  else if(Phase==3){Steer(Committed,4.4);if(Distance2D(p)<48&&CheckSight(p)){p.DamageMobj(self,self,80,'Heavy');Phase=4;Age=0;Vel.X=0;Vel.Y=0;}else if(Age>=14){Phase=4;Age=0;}}
  else if(Phase==5){if(Age==1){Height=88;A_StartSound("c5/wood",CHAN_BODY);Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY,"C7 HOLLOW_ROOT_BLOW_WARN tic=%d",level.time);}
   if(Age>=42){Vector2 lane=Committed.XY-Pos.XY;Vector2 victim=p.Pos.XY-Pos.XY;double facing=atan2(lane.Y,lane.X);if(victim.Length()<112&&abs(deltaangle(facing,AngleTo(p)))<24&&CheckSight(p))p.DamageMobj(self,self,100,'Heavy');Phase=6;Age=0;Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY,"C7 HOLLOW_ROOT_BLOW tic=%d",level.time);}}
  else if(Phase==6&&Age>=35){Phase=1;Age=0;Height=32;}
  else if(Phase==4&&Age>=56){Phase=1;Age=0;SetStateLabel('Crawl');}
 }
 override int DamageMobj(Actor inflictor,Actor source,int damage,Name mod,int flags,double angle){Active=true;ArtHit=12;return Super.DamageMobj(inflictor,source,damage,mod,flags,angle);}
 override void Die(Actor source,Actor inflictor,int flags,Name mod){
  Super.Die(source,inflictor,flags,mod);bSHOOTABLE=false;
  for(int j=0;j<12;j++){double a=j*137.5;let piece=C7Debris(Actor.Spawn('C7Debris',Pos+(cos(a)*12,sin(a)*12,12+(j%4)*12)));if(piece){piece.Kind=j%3;piece.Angle=a;piece.Vel=(cos(a)*(.8+(j%3)*.3),sin(a)*(.8+(j%3)*.3),1.+(j%4)*.4);}}
 }
}

class C5Stone:C5Enemy {
 C5Player Captive;int Stage,GripAge,GripDamage;C5Hollow Partner;
 Default {Health 100;Radius 18;Height 64;Scale .1044;}
 States {Spawn:E2IP ABCD 7;Loop;Grab:E2AP ABCD 7;Loop;Stagger:E2IP B -1;Stop;Death:TNT1 A 1;Stop;}
 void Release(){if(Captive){Captive.Grip=null;Captive.Immune=70;}Captive=null;Stage=3;GripAge=0;SetStateLabel('Stagger');A_StartSound("c5/release",CHAN_BODY);Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY, "C5 GRAPPLE_RELEASE tic=%d",level.time);}
 override void Tick(){Super.Tick();if(health<=0)return;Vel.X=0;Vel.Y=0;let p=C5Player(players[0].mo);if(!p||p.health<=0){if(Captive)Release();return;}
  if(!Active)return;
  if(Partner)Partner.Active=true;
  if(Stage==0){Steer(p.Pos,ChaseSpeed);if(Distance2D(p)<100&&CheckSight(p)){Stage=4;GripAge=0;Committed=p.Pos;A_StartSound("c5/grip",CHAN_VOICE);SetStateLabel('Grab');Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY, "C5 REDEAD_REACH_WARN tic=%d",level.time);}}
  else if(Stage==4){GripAge++;if(GripAge>=35){if(Distance2D(p)<64&&p.Immune==0&&CheckSight(p)&&abs(deltaangle(Angle,AngleTo(p)))<65){Captive=p;p.Grip=self;Stage=1;GripAge=0;GripDamage=0;Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY, "C5 SNARE tic=%d",level.time);}else{Stage=3;GripAge=0;}}}
  else if(Stage==1||Stage==2){GripAge++;if(!Captive||Captive.health<=0||Distance2D(Captive)>100){Release();return;}if(Captive.MoveBurst>0){Release();return;}
   if(Stage==1&&GripAge>=28){Captive.DamageMobj(self,self,20,'Grip');Stage=2;GripAge=0;Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY, "C5 BODY_LOCK no_view_steering tic=%d",level.time);}
   else if(Stage==2&&GripAge>=35){Captive.DamageMobj(self,self,65,'Heavy');Release();}}
  else if(Stage==3){if(++GripAge>=70){Stage=0;SetStateLabel('Spawn');}}
 }
 override void PictureHit(Actor shooter,Vector3 origin,Vector3 dir,int kind,int damage){double t=(Pos.XY-origin.XY).Length();Vector3 point=origin+dir*t;double z=point.Z-Pos.Z;if(z>=32&&z<=56&&(Stage==1||Stage==2)){GripDamage+=damage;if(GripDamage>=18)Release();}Super.PictureHit(shooter,origin,dir,kind,damage);}
 override int DamageMobj(Actor inflictor,Actor source,int damage,Name mod,int flags,double angle){Active=true;if(Partner)Partner.Active=true;return Super.DamageMobj(inflictor,source,damage,mod,flags,angle);}
 override void Die(Actor source,Actor inflictor,int flags,Name mod){if(Captive)Release();Super.Die(source,inflictor,flags,mod);}
 override void OnDestroy(){if(Captive)Release();Super.OnDestroy();}
}
class C5Arm:C5Enemy {
 C5Coordinator Coordinator;bool Controlled,Crippled,Core;int Pose,Band,Yaw,Legs,Collar,Cage,Frenzy,Role,CoreHP,ArtHit,Collapse;Vector2 History[8];int HistoryAge,Recover,Blocked,FlankUntil,NavAge;Array<int> PathDist;
 override void PostBeginPlay(){Super.PostBeginPlay();Core=true;Legs=26;Collar=24;Cage=50;CoreHP=22;}
 Default {Health 60;Radius 18;Height 56;Scale .75;}
 States {Spawn:Q20I A -1;Stop;Death:TNT1 A 1;Stop;}
 bool BodyPixel(double x,double z){int id=(Pose*5+Band)*8+Yaw;int px=int(floor(x/.75+32)),py=int(floor(C5Mask.Foot(id)-z/.75));if(px<0||px>=64||py<0||py>=96)return false;return ((C5Mask.BodyBits((id*96+py)*4+px/16)>>(px%16))&1)!=0;}
 bool CorePixel(double x,double z){int id=(Pose*5+Band)*8+Yaw;int px=int(floor(x/.75+32)),py=int(floor(C5Mask.Foot(id)-z/.75));if(px<0||px>=64||py<0||py>=96)return false;int k=id*96+py;return Core&&C5Mask.Left(k)>=0&&px>=C5Mask.Left(k)&&px<=C5Mask.Right(k);}

 bool RegionPixel(double x,double z,int region){int id=(Pose*5+Band)*8+Yaw;int px=int(floor(x/.75+32)),py=int(floor(C5Mask.Foot(id)-z/.75));if(px<0||px>=64||py<0||py>=96)return false;return ((C5Mask.RegionBits((((id*96+py)*4+px/16)*4)+region-1)>>(px%16))&1)!=0;}
 override void Tick(){Super.Tick();if(health<=0){
 Collapse++;Vel.X=0;Vel.Y=0;let viewer=players[0].mo;
 if(viewer){Band=clamp(int(round(atan2(viewer.player.viewz-Pos.Z-14,Distance2D(viewer))/22.5))+2,0,4);Yaw=(int(round(deltaangle(Angle,AngleTo(viewer))/45))+8)%8;}
 sprite=GetSpriteIndex(String.Format("Q%d%dD",Band,Yaw));frame=min(3,Collapse/9);
 if(Collapse==28)A_StartSound("c7/settle",CHAN_BODY);
 if(Collapse==36)Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY,"C7 HEAP_SETTLED role=%d tic=%d pos=(%.2f,%.2f,%.2f)",Role,level.time,Pos.X,Pos.Y,Pos.Z);
 return;}Vel.X=0;Vel.Y=0;Age++;let p=C5Player(players[0].mo);if(!p||p.health<=0)return;Pose=Crippled?1:0;
  if(Frenzy>0){Pose=2;if(Frenzy--==18){let it=ThinkerIterator.Create('C5Arm');C5Arm a;while(a=C5Arm(it.Next()))if(a!=self&&a.health>0&&Distance2D(a)<80){a.DamageMobj(self,self,80,'Frenzy');break;}}}
  else if(Controlled){int clock=level.time-Coordinator.CoordinateAt;int beat=clock%280;
   if(beat>=175&&beat<210){Pose=2;if(beat==175)A_StartSound("c5/tick",CHAN_BODY);}
   else if(beat==210){if(Distance2D(p)<64&&CheckSight(p))p.DamageMobj(self,self,80,'Heavy');Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY, "C5 ARM_STRIKE role=%d tic=%d",Role,level.time);}
   else if(beat<175){Vector3 goal=p.Pos;double a=Coordinator.GroupYaw+90;if(Distance2D(p)>128){goal.X+=cos(a)*(Role-1)*72;goal.Y+=sin(a)*(Role-1)*72;}PackSteer(goal,Crippled?.45:1.9);}
  }else if(Age%113<35){double a=Role*120+Age/113*67;Vector3 goal=Home+(cos(a)*45,sin(a)*45,0);Steer(goal,.25);}
  Band=clamp(int(round(atan2(p.player.viewz-Pos.Z-28,Distance2D(p))/22.5))+2,0,4);Yaw=(int(round(deltaangle(Angle,AngleTo(p))/45))+8)%8;int artRole=0,artFrame=(Age/9)%4;
 if(Frenzy>0)artRole=6;
 else if(Crippled)artRole=5;
 else if(Controlled){int beat=(level.time-Coordinator.CoordinateAt)%280;
 if(beat>=175&&beat<210){artRole=2;artFrame=min(3,(beat-175)/9);}
 else if(beat>=210&&beat<231){artRole=3;artFrame=min(3,(beat-210)/6);}
 else if(beat<175){artRole=1;artFrame=(Age/5)%4;}}
 if(ArtHit>0){artRole=4;artFrame=min(3,(8-ArtHit)/2);ArtHit--;}
 String artCode=artRole==0?"I":artRole==1?"V":artRole==2?"W":artRole==3?"S":artRole==4?"H":artRole==5?"C":"F";
 Pose=artRole*4+artFrame;sprite=GetSpriteIndex(String.Format("Q%d%d%s",Band,Yaw,artCode));frame=artFrame;
 }
 override void PictureHit(Actor shooter,Vector3 origin,Vector3 dir,int kind,int damage){double forward=atan2(Pos.Y-origin.Y,Pos.X-origin.X);Vector3 f=(cos(forward),sin(forward),0),right=(f.Y,-f.X,0);double den=dir.X*f.X+dir.Y*f.Y;if(abs(den)<.0001)return;double t=((Pos.X-origin.X)*f.X+(Pos.Y-origin.Y)*f.Y)/den;Vector3 q=origin+dir*t;double x=(q.X-Pos.X)*right.X+(q.Y-Pos.Y)*right.Y,z=q.Z-Pos.Z;Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY,"C7 ARM_SHOT role=%d tic=%d x=%.2f z=%.2f body=%d core=%d damage=%d",Role,level.time,x,z,BodyPixel(x,z),CorePixel(x,z),damage);if(!BodyPixel(x,z))return;ArtHit=8;
  if(CorePixel(x,z)){CoreHP-=int(damage*(kind==1?2.2:1));if(CoreHP<=0){Core=false;Fall();return;}}
  else if(RegionPixel(x,z,2)){Legs-=int(damage*(kind==0?1.75:.8));if(Legs<=0){Crippled=true;Height=27;Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY, "C5 ARM_CRIPPLED no_lunge");}}
  else if(RegionPixel(x,z,3)&&Controlled){Collar-=damage;if(Collar<=0){Frenzy=35;Controlled=false;Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY, "C5 COLLAR_FRENZY");}}
  else{Cage-=int(damage*.85);if(Cage<=0)Fall();}
 }
 override void Die(Actor source,Actor inflictor,int flags,Name mod){Fall();}
 void Fall(){if(Collapse>0)return;Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY, "C5 ARM_SCRAP tic=%d",level.time);health=0;bSOLID=false;bSHOOTABLE=false;Vel=(0,0,0);Collapse=1;Height=8;}
 void PackSteer(Vector3 goal,double speed){
  let prey=players[0].mo;
  if(prey&&Distance2D(prey)<48&&CheckSight(prey)){Vel.X=0;Vel.Y=0;HistoryAge=0;Blocked=0;Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY,"C7 STRIKE_SLOT role=%d tic=%d x=%.3f y=%.3f",Role,level.time,Pos.X,Pos.Y);return;}
  if(!Coordinator.Nav)Coordinator.Nav=C7Nav(Actor.Spawn('C7Nav',Pos));
  let nav=Coordinator.Nav;if(!nav.Ready)nav.Build();
  int here=nav.Cell(Pos.XY);int targetCell=nav.Nearest(goal.XY);
  Vector2 previous=History[HistoryAge%8];History[HistoryAge%8]=Pos.XY;HistoryAge++;
  double displacement=(Pos.XY-previous).Length();bool pinned=HistoryAge>8&&displacement<speed*2;
  if(pinned){Blocked++;if(Blocked>=3&&Recover==0&&(Blocked-3)%14==0){Recover=10;FlankUntil=level.time+70;NavAge=0;Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY,"C7 RECOVER role=%d tic=%d pos=(%.2f,%.2f)",Role,level.time,Pos.X,Pos.Y);}}
  else Blocked=0;
  if(level.time<FlankUntil&&prey&&Distance2D(prey)>80){let player=players[0].mo;double theta=Coordinator.GroupYaw+(Role==1?90:Role==0?155:-155);targetCell=nav.Nearest(player.Pos.XY+(cos(theta)*112,sin(theta)*112));}
  if(NavAge--<=0||PathDist.Size()==0){nav.Flood(targetCell,PathDist);NavAge=7;}
  Vector2 wish=goal.XY-Pos.XY;
  if(here>=0&&PathDist.Size()>0){int next=here;int best=PathDist[here];for(int j=0;j<4;j++){int nb=nav.Neighbor(here,j);if(nb>=0&&PathDist[nb]>=0&&PathDist[nb]<best){best=PathDist[nb];next=nb;}}
   if(next!=here)wish=nav.Point(next)-Pos.XY;
  }
  if(wish.Length()>.01)wish=wish.Unit();
  Vector2 separation=(0,0);
  for(int i=0;i<Coordinator.Group.Size();i++){let other=Coordinator.Group[i];if(!other||other==self||other.health<=0)continue;Vector2 away=Pos.XY-other.Pos.XY;double d=away.Length();if(d>0&&d<58){away/=d;double weight=(58-d)/22;separation+=weight*(away*.8+(-away.Y,away.X)*.55);}}
  wish+=separation*.65;
  if(Recover>0){Recover--;double turn=Blocked>14?150:75;double a=atan2(wish.Y,wish.X)+turn;wish=(cos(a),sin(a))+separation*.5;}
  if(wish.Length()<.01)return;double aim=atan2(wish.Y,wish.X);bool found=false;
  // CheckMove tests the actual actor disc; lookahead includes an extra 4 u clearance.
  for(int j=0;j<13;j++){double off=j==0?0:((j+1)/2)*15*(j%2==1?1:-1);double a=aim+off;Vector2 step=(cos(a),sin(a));
   if(CheckMove(Pos.XY+step*(speed*2+4))&&CheckMove(Pos.XY+step*speed)){Angle=a;Vel.X=step.X*speed;Vel.Y=step.Y*speed;found=true;break;}}
  if(!found){Vel.X=0;Vel.Y=0;NavAge=0;}
  Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY,"C7 CHASE role=%d tic=%d x=%.3f y=%.3f speed=%.2f displacement=%.3f blocked=%d recover=%d",Role,level.time,Pos.X,Pos.Y,speed,displacement,Blocked,Recover);
 }
}
class C5Coordinator:Actor {
 C7Nav Nav;Array<C5Arm> Group;int TickAt,CoordinateAt,NextTick;double GroupYaw;Array<DynamicLight> Lamps;
 Default {+NOINTERACTION +NOGRAVITY Radius 1;Height 1;}
 States{Spawn:TNT1 A -1;Stop;}
 override void Tick(){Super.Tick();let p=C5Player(players[0].mo);if(!p||p.health<=0)return;
  if(TickAt==0){if(Distance2D(p)<800&&(p.Pos.X>600||p.MoveNoise>1)){TickAt=level.time;CoordinateAt=TickAt+175;Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY, "C5 CERAMIC_WARNING tic=%d",level.time);}else return;}
  if(level.time>=NextTick&&level.time<CoordinateAt+70){A_StartSound("c5/tick",CHAN_BODY,0,.8);NextTick=level.time+12;}
  for(int j=0;j<Lamps.Size();j++){double f=clamp((level.time-TickAt-j*70)/140.,0.,1.);Lamps[j].args[3]=int(55*(1-f));}
  if(level.time>=CoordinateAt){GroupYaw=p.Angle;for(int i=0;i<Group.Size();i++)if(Group[i]&&Group[i].health>0)Group[i].Controlled=true;}
 }
}
class C5Pickup:Actor {
 int Kind;
 Default {Radius 5;Height 6;XScale .125;YScale .1041667;+NOGRAVITY +NOBLOOD}
 States{Spawn:C5TI A -1;Stop;}
}
class C5Encounter:EventHandler {
 C5Hollow Hollow;C5Stone Stone;C5Coordinator Group;Array<int> BaySectors,GallerySectors;int PairAt;bool LastUse;
 void Pair(){Hollow=C5Hollow(Actor.Spawn('C5Hollow',(32,976,64)));Stone=C5Stone(Actor.Spawn('C5Stone',(-136,864,64)));if(!Hollow||!Stone){if(Hollow)Hollow.Destroy();if(Stone)Stone.Destroy();Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY, "C5 ERROR: mandatory pair spawn failed");}Stone.Partner=Hollow;Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY, "C5 PAIRED Hollow=1 StoneReDead=1");}
 override void WorldLoaded(WorldEvent e){if(level.levelnum!=4||e.IsSaveGame)return;Pair();
  Group=C5Coordinator(Actor.Spawn('C5Coordinator',(920,560,96)));for(int i=0;i<3;i++){let a=C5Arm(Actor.Spawn('C5Arm',(870+(i%2)*100,280+i*100,64)));a.Role=i;a.Coordinator=Group;Group.Group.Push(a);let lamp=DynamicLight(Actor.Spawn('PointLight',(900,160+i*190,180)));lamp.args[0]=150;lamp.args[1]=195;lamp.args[2]=220;lamp.args[3]=55;Group.Lamps.Push(lamp);}
  let q0=C5Pickup(Actor.Spawn("C5Pickup",(-48,-528,26)));q0.Kind=0;q0.sprite=Actor.GetSpriteIndex("C5T0");
let q1=C5Pickup(Actor.Spawn("C5Pickup",(48,-432,26)));q1.Kind=1;q1.sprite=Actor.GetSpriteIndex("C5T1");
let q2=C5Pickup(Actor.Spawn("C5Pickup",(-48,-336,26)));q2.Kind=2;q2.sprite=Actor.GetSpriteIndex("C5T2");
BaySectors.Push(43);level.sectors[43].SetColor(Color(125,190,180));
GallerySectors.Push(12);
let a=Actor.Spawn("C5BayPlate",(-264,842,160));a.Angle=180;let lp=DynamicLight(Actor.Spawn("PointLight",(80,1000,155)));lp.args[0]=95;lp.args[1]=190;lp.args[2]=165;lp.args[3]=100;
 }
 override void WorldTick(){if(level.levelnum!=4)return;let p=C5Player(players[0].mo);if(!p)return;
  if(PairAt==0&&Stone&&(Stone.Active||Stone.Notice(p))){PairAt=level.time;Stone.Active=true;Hollow.Active=true;Stone.A_StartSound("c5/grip",CHAN_VOICE);Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY, "C5 PAIR_ALERT tic=%d",level.time);}
  if(PairAt>0){double t=clamp((level.time-PairAt)/280.,0.,1.);for(int i=0;i<BaySectors.Size();i++){let s=level.sectors[BaySectors[i]];s.SetLightLevel(int(116-24*t));s.SetFade(Color(int(8*t),int(19*t),int(18*t)));s.SetFogDensity(int(42*t));}}
  if(Group&&Group.TickAt>0){double t=clamp((level.time-Group.TickAt)/280.,0.,1.);for(int i=0;i<GallerySectors.Size();i++){let s=level.sectors[GallerySectors[i]];s.SetLightLevel(int(152-40*t));s.SetFade(Color(int(9*t),int(17*t),int(18*t)));s.SetFogDensity(int(36*t));}}
  bool use=(p.player.cmd.buttons&BT_USE)!=0;if(use&&!LastUse){let it=ThinkerIterator.Create('C5Pickup');C5Pickup q;C5Pickup best;double distance=56;while(q=C5Pickup(it.Next()))if(p.Distance2D(q)<distance&&p.CheckSight(q)){best=q;distance=p.Distance2D(q);}if(best){if(best.Kind==0)p.Medical++;else if(best.Kind==1)p.GiveInventory('Clip',20);else p.Salvage+=3;p.A_StartSound("c5/take",CHAN_ITEM);Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY, "C5 PHYSICAL_PICKUP kind=%d tic=%d",best.Kind,level.time);best.Destroy();}}LastUse=use;
 }
}

class C5SpriteRegistry:Actor {States {Spawn:TNT1 A -1;Stop;Register:Q00I A 0; Q00C A 0; Q00W A 0; Q01I A 0; Q01C A 0; Q01W A 0; Q02I A 0; Q02C A 0; Q02W A 0; Q03I A 0; Q03C A 0; Q03W A 0; Q04I A 0; Q04C A 0; Q04W A 0; Q05I A 0; Q05C A 0; Q05W A 0; Q06I A 0; Q06C A 0; Q06W A 0; Q07I A 0; Q07C A 0; Q07W A 0; Q10I A 0; Q10C A 0; Q10W A 0; Q11I A 0; Q11C A 0; Q11W A 0; Q12I A 0; Q12C A 0; Q12W A 0; Q13I A 0; Q13C A 0; Q13W A 0; Q14I A 0; Q14C A 0; Q14W A 0; Q15I A 0; Q15C A 0; Q15W A 0; Q16I A 0; Q16C A 0; Q16W A 0; Q17I A 0; Q17C A 0; Q17W A 0; Q20I A 0; Q20C A 0; Q20W A 0; Q21I A 0; Q21C A 0; Q21W A 0; Q22I A 0; Q22C A 0; Q22W A 0; Q23I A 0; Q23C A 0; Q23W A 0; Q24I A 0; Q24C A 0; Q24W A 0; Q25I A 0; Q25C A 0; Q25W A 0; Q26I A 0; Q26C A 0; Q26W A 0; Q27I A 0; Q27C A 0; Q27W A 0; Q30I A 0; Q30C A 0; Q30W A 0; Q31I A 0; Q31C A 0; Q31W A 0; Q32I A 0; Q32C A 0; Q32W A 0; Q33I A 0; Q33C A 0; Q33W A 0; Q34I A 0; Q34C A 0; Q34W A 0; Q35I A 0; Q35C A 0; Q35W A 0; Q36I A 0; Q36C A 0; Q36W A 0; Q37I A 0; Q37C A 0; Q37W A 0; Q40I A 0; Q40C A 0; Q40W A 0; Q41I A 0; Q41C A 0; Q41W A 0; Q42I A 0; Q42C A 0; Q42W A 0; Q43I A 0; Q43C A 0; Q43W A 0; Q44I A 0; Q44C A 0; Q44W A 0; Q45I A 0; Q45C A 0; Q45W A 0; Q46I A 0; Q46C A 0; Q46W A 0; Q47I A 0; Q47C A 0; Q47W A 0; C5T0 A 0; C5T1 A 0; C5T2 A 0; Stop;}}
class C6ArtRegistry:Actor {States {Spawn:TNT1 A -1;Stop;Register:K00I ABCD 0;K00F ABCD 0;K00C ABCD 0;K00T ABCD 0;K00P ABCD 0;K00R ABCD 0;K00H ABCD 0;K00D ABCD 0;K00X ABCD 0;K01I ABCD 0;K01F ABCD 0;K01C ABCD 0;K01T ABCD 0;K01P ABCD 0;K01R ABCD 0;K01H ABCD 0;K01D ABCD 0;K01X ABCD 0;K02I ABCD 0;K02F ABCD 0;K02C ABCD 0;K02T ABCD 0;K02P ABCD 0;K02R ABCD 0;K02H ABCD 0;K02D ABCD 0;K02X ABCD 0;K03I ABCD 0;K03F ABCD 0;K03C ABCD 0;K03T ABCD 0;K03P ABCD 0;K03R ABCD 0;K03H ABCD 0;K03D ABCD 0;K03X ABCD 0;K04I ABCD 0;K04F ABCD 0;K04C ABCD 0;K04T ABCD 0;K04P ABCD 0;K04R ABCD 0;K04H ABCD 0;K04D ABCD 0;K04X ABCD 0;K05I ABCD 0;K05F ABCD 0;K05C ABCD 0;K05T ABCD 0;K05P ABCD 0;K05R ABCD 0;K05H ABCD 0;K05D ABCD 0;K05X ABCD 0;K06I ABCD 0;K06F ABCD 0;K06C ABCD 0;K06T ABCD 0;K06P ABCD 0;K06R ABCD 0;K06H ABCD 0;K06D ABCD 0;K06X ABCD 0;K07I ABCD 0;K07F ABCD 0;K07C ABCD 0;K07T ABCD 0;K07P ABCD 0;K07R ABCD 0;K07H ABCD 0;K07D ABCD 0;K07X ABCD 0;K10I ABCD 0;K10F ABCD 0;K10C ABCD 0;K10T ABCD 0;K10P ABCD 0;K10R ABCD 0;K10H ABCD 0;K10D ABCD 0;K10X ABCD 0;K11I ABCD 0;K11F ABCD 0;K11C ABCD 0;K11T ABCD 0;K11P ABCD 0;K11R ABCD 0;K11H ABCD 0;K11D ABCD 0;K11X ABCD 0;K12I ABCD 0;K12F ABCD 0;K12C ABCD 0;K12T ABCD 0;K12P ABCD 0;K12R ABCD 0;K12H ABCD 0;K12D ABCD 0;K12X ABCD 0;K13I ABCD 0;K13F ABCD 0;K13C ABCD 0;K13T ABCD 0;K13P ABCD 0;K13R ABCD 0;K13H ABCD 0;K13D ABCD 0;K13X ABCD 0;K14I ABCD 0;K14F ABCD 0;K14C ABCD 0;K14T ABCD 0;K14P ABCD 0;K14R ABCD 0;K14H ABCD 0;K14D ABCD 0;K14X ABCD 0;K15I ABCD 0;K15F ABCD 0;K15C ABCD 0;K15T ABCD 0;K15P ABCD 0;K15R ABCD 0;K15H ABCD 0;K15D ABCD 0;K15X ABCD 0;K16I ABCD 0;K16F ABCD 0;K16C ABCD 0;K16T ABCD 0;K16P ABCD 0;K16R ABCD 0;K16H ABCD 0;K16D ABCD 0;K16X ABCD 0;K17I ABCD 0;K17F ABCD 0;K17C ABCD 0;K17T ABCD 0;K17P ABCD 0;K17R ABCD 0;K17H ABCD 0;K17D ABCD 0;K17X ABCD 0;K20I ABCD 0;K20F ABCD 0;K20C ABCD 0;K20T ABCD 0;K20P ABCD 0;K20R ABCD 0;K20H ABCD 0;K20D ABCD 0;K20X ABCD 0;K21I ABCD 0;K21F ABCD 0;K21C ABCD 0;K21T ABCD 0;K21P ABCD 0;K21R ABCD 0;K21H ABCD 0;K21D ABCD 0;K21X ABCD 0;K22I ABCD 0;K22F ABCD 0;K22C ABCD 0;K22T ABCD 0;K22P ABCD 0;K22R ABCD 0;K22H ABCD 0;K22D ABCD 0;K22X ABCD 0;K23I ABCD 0;K23F ABCD 0;K23C ABCD 0;K23T ABCD 0;K23P ABCD 0;K23R ABCD 0;K23H ABCD 0;K23D ABCD 0;K23X ABCD 0;K24I ABCD 0;K24F ABCD 0;K24C ABCD 0;K24T ABCD 0;K24P ABCD 0;K24R ABCD 0;K24H ABCD 0;K24D ABCD 0;K24X ABCD 0;K25I ABCD 0;K25F ABCD 0;K25C ABCD 0;K25T ABCD 0;K25P ABCD 0;K25R ABCD 0;K25H ABCD 0;K25D ABCD 0;K25X ABCD 0;K26I ABCD 0;K26F ABCD 0;K26C ABCD 0;K26T ABCD 0;K26P ABCD 0;K26R ABCD 0;K26H ABCD 0;K26D ABCD 0;K26X ABCD 0;K27I ABCD 0;K27F ABCD 0;K27C ABCD 0;K27T ABCD 0;K27P ABCD 0;K27R ABCD 0;K27H ABCD 0;K27D ABCD 0;K27X ABCD 0;K30I ABCD 0;K30F ABCD 0;K30C ABCD 0;K30T ABCD 0;K30P ABCD 0;K30R ABCD 0;K30H ABCD 0;K30D ABCD 0;K30X ABCD 0;K31I ABCD 0;K31F ABCD 0;K31C ABCD 0;K31T ABCD 0;K31P ABCD 0;K31R ABCD 0;K31H ABCD 0;K31D ABCD 0;K31X ABCD 0;K32I ABCD 0;K32F ABCD 0;K32C ABCD 0;K32T ABCD 0;K32P ABCD 0;K32R ABCD 0;K32H ABCD 0;K32D ABCD 0;K32X ABCD 0;K33I ABCD 0;K33F ABCD 0;K33C ABCD 0;K33T ABCD 0;K33P ABCD 0;K33R ABCD 0;K33H ABCD 0;K33D ABCD 0;K33X ABCD 0;K34I ABCD 0;K34F ABCD 0;K34C ABCD 0;K34T ABCD 0;K34P ABCD 0;K34R ABCD 0;K34H ABCD 0;K34D ABCD 0;K34X ABCD 0;K35I ABCD 0;K35F ABCD 0;K35C ABCD 0;K35T ABCD 0;K35P ABCD 0;K35R ABCD 0;K35H ABCD 0;K35D ABCD 0;K35X ABCD 0;K36I ABCD 0;K36F ABCD 0;K36C ABCD 0;K36T ABCD 0;K36P ABCD 0;K36R ABCD 0;K36H ABCD 0;K36D ABCD 0;K36X ABCD 0;K37I ABCD 0;K37F ABCD 0;K37C ABCD 0;K37T ABCD 0;K37P ABCD 0;K37R ABCD 0;K37H ABCD 0;K37D ABCD 0;K37X ABCD 0;K40I ABCD 0;K40F ABCD 0;K40C ABCD 0;K40T ABCD 0;K40P ABCD 0;K40R ABCD 0;K40H ABCD 0;K40D ABCD 0;K40X ABCD 0;K41I ABCD 0;K41F ABCD 0;K41C ABCD 0;K41T ABCD 0;K41P ABCD 0;K41R ABCD 0;K41H ABCD 0;K41D ABCD 0;K41X ABCD 0;K42I ABCD 0;K42F ABCD 0;K42C ABCD 0;K42T ABCD 0;K42P ABCD 0;K42R ABCD 0;K42H ABCD 0;K42D ABCD 0;K42X ABCD 0;K43I ABCD 0;K43F ABCD 0;K43C ABCD 0;K43T ABCD 0;K43P ABCD 0;K43R ABCD 0;K43H ABCD 0;K43D ABCD 0;K43X ABCD 0;K44I ABCD 0;K44F ABCD 0;K44C ABCD 0;K44T ABCD 0;K44P ABCD 0;K44R ABCD 0;K44H ABCD 0;K44D ABCD 0;K44X ABCD 0;K45I ABCD 0;K45F ABCD 0;K45C ABCD 0;K45T ABCD 0;K45P ABCD 0;K45R ABCD 0;K45H ABCD 0;K45D ABCD 0;K45X ABCD 0;K46I ABCD 0;K46F ABCD 0;K46C ABCD 0;K46T ABCD 0;K46P ABCD 0;K46R ABCD 0;K46H ABCD 0;K46D ABCD 0;K46X ABCD 0;K47I ABCD 0;K47F ABCD 0;K47C ABCD 0;K47T ABCD 0;K47P ABCD 0;K47R ABCD 0;K47H ABCD 0;K47D ABCD 0;K47X ABCD 0;Q00I ABCD 0;Q00V ABCD 0;Q00W ABCD 0;Q00S ABCD 0;Q00H ABCD 0;Q00C ABCD 0;Q00F ABCD 0;Q00D ABCD 0;Q01I ABCD 0;Q01V ABCD 0;Q01W ABCD 0;Q01S ABCD 0;Q01H ABCD 0;Q01C ABCD 0;Q01F ABCD 0;Q01D ABCD 0;Q02I ABCD 0;Q02V ABCD 0;Q02W ABCD 0;Q02S ABCD 0;Q02H ABCD 0;Q02C ABCD 0;Q02F ABCD 0;Q02D ABCD 0;Q03I ABCD 0;Q03V ABCD 0;Q03W ABCD 0;Q03S ABCD 0;Q03H ABCD 0;Q03C ABCD 0;Q03F ABCD 0;Q03D ABCD 0;Q04I ABCD 0;Q04V ABCD 0;Q04W ABCD 0;Q04S ABCD 0;Q04H ABCD 0;Q04C ABCD 0;Q04F ABCD 0;Q04D ABCD 0;Q05I ABCD 0;Q05V ABCD 0;Q05W ABCD 0;Q05S ABCD 0;Q05H ABCD 0;Q05C ABCD 0;Q05F ABCD 0;Q05D ABCD 0;Q06I ABCD 0;Q06V ABCD 0;Q06W ABCD 0;Q06S ABCD 0;Q06H ABCD 0;Q06C ABCD 0;Q06F ABCD 0;Q06D ABCD 0;Q07I ABCD 0;Q07V ABCD 0;Q07W ABCD 0;Q07S ABCD 0;Q07H ABCD 0;Q07C ABCD 0;Q07F ABCD 0;Q07D ABCD 0;Q10I ABCD 0;Q10V ABCD 0;Q10W ABCD 0;Q10S ABCD 0;Q10H ABCD 0;Q10C ABCD 0;Q10F ABCD 0;Q10D ABCD 0;Q11I ABCD 0;Q11V ABCD 0;Q11W ABCD 0;Q11S ABCD 0;Q11H ABCD 0;Q11C ABCD 0;Q11F ABCD 0;Q11D ABCD 0;Q12I ABCD 0;Q12V ABCD 0;Q12W ABCD 0;Q12S ABCD 0;Q12H ABCD 0;Q12C ABCD 0;Q12F ABCD 0;Q12D ABCD 0;Q13I ABCD 0;Q13V ABCD 0;Q13W ABCD 0;Q13S ABCD 0;Q13H ABCD 0;Q13C ABCD 0;Q13F ABCD 0;Q13D ABCD 0;Q14I ABCD 0;Q14V ABCD 0;Q14W ABCD 0;Q14S ABCD 0;Q14H ABCD 0;Q14C ABCD 0;Q14F ABCD 0;Q14D ABCD 0;Q15I ABCD 0;Q15V ABCD 0;Q15W ABCD 0;Q15S ABCD 0;Q15H ABCD 0;Q15C ABCD 0;Q15F ABCD 0;Q15D ABCD 0;Q16I ABCD 0;Q16V ABCD 0;Q16W ABCD 0;Q16S ABCD 0;Q16H ABCD 0;Q16C ABCD 0;Q16F ABCD 0;Q16D ABCD 0;Q17I ABCD 0;Q17V ABCD 0;Q17W ABCD 0;Q17S ABCD 0;Q17H ABCD 0;Q17C ABCD 0;Q17F ABCD 0;Q17D ABCD 0;Q20I ABCD 0;Q20V ABCD 0;Q20W ABCD 0;Q20S ABCD 0;Q20H ABCD 0;Q20C ABCD 0;Q20F ABCD 0;Q20D ABCD 0;Q21I ABCD 0;Q21V ABCD 0;Q21W ABCD 0;Q21S ABCD 0;Q21H ABCD 0;Q21C ABCD 0;Q21F ABCD 0;Q21D ABCD 0;Q22I ABCD 0;Q22V ABCD 0;Q22W ABCD 0;Q22S ABCD 0;Q22H ABCD 0;Q22C ABCD 0;Q22F ABCD 0;Q22D ABCD 0;Q23I ABCD 0;Q23V ABCD 0;Q23W ABCD 0;Q23S ABCD 0;Q23H ABCD 0;Q23C ABCD 0;Q23F ABCD 0;Q23D ABCD 0;Q24I ABCD 0;Q24V ABCD 0;Q24W ABCD 0;Q24S ABCD 0;Q24H ABCD 0;Q24C ABCD 0;Q24F ABCD 0;Q24D ABCD 0;Q25I ABCD 0;Q25V ABCD 0;Q25W ABCD 0;Q25S ABCD 0;Q25H ABCD 0;Q25C ABCD 0;Q25F ABCD 0;Q25D ABCD 0;Q26I ABCD 0;Q26V ABCD 0;Q26W ABCD 0;Q26S ABCD 0;Q26H ABCD 0;Q26C ABCD 0;Q26F ABCD 0;Q26D ABCD 0;Q27I ABCD 0;Q27V ABCD 0;Q27W ABCD 0;Q27S ABCD 0;Q27H ABCD 0;Q27C ABCD 0;Q27F ABCD 0;Q27D ABCD 0;Q30I ABCD 0;Q30V ABCD 0;Q30W ABCD 0;Q30S ABCD 0;Q30H ABCD 0;Q30C ABCD 0;Q30F ABCD 0;Q30D ABCD 0;Q31I ABCD 0;Q31V ABCD 0;Q31W ABCD 0;Q31S ABCD 0;Q31H ABCD 0;Q31C ABCD 0;Q31F ABCD 0;Q31D ABCD 0;Q32I ABCD 0;Q32V ABCD 0;Q32W ABCD 0;Q32S ABCD 0;Q32H ABCD 0;Q32C ABCD 0;Q32F ABCD 0;Q32D ABCD 0;Q33I ABCD 0;Q33V ABCD 0;Q33W ABCD 0;Q33S ABCD 0;Q33H ABCD 0;Q33C ABCD 0;Q33F ABCD 0;Q33D ABCD 0;Q34I ABCD 0;Q34V ABCD 0;Q34W ABCD 0;Q34S ABCD 0;Q34H ABCD 0;Q34C ABCD 0;Q34F ABCD 0;Q34D ABCD 0;Q35I ABCD 0;Q35V ABCD 0;Q35W ABCD 0;Q35S ABCD 0;Q35H ABCD 0;Q35C ABCD 0;Q35F ABCD 0;Q35D ABCD 0;Q36I ABCD 0;Q36V ABCD 0;Q36W ABCD 0;Q36S ABCD 0;Q36H ABCD 0;Q36C ABCD 0;Q36F ABCD 0;Q36D ABCD 0;Q37I ABCD 0;Q37V ABCD 0;Q37W ABCD 0;Q37S ABCD 0;Q37H ABCD 0;Q37C ABCD 0;Q37F ABCD 0;Q37D ABCD 0;Q40I ABCD 0;Q40V ABCD 0;Q40W ABCD 0;Q40S ABCD 0;Q40H ABCD 0;Q40C ABCD 0;Q40F ABCD 0;Q40D ABCD 0;Q41I ABCD 0;Q41V ABCD 0;Q41W ABCD 0;Q41S ABCD 0;Q41H ABCD 0;Q41C ABCD 0;Q41F ABCD 0;Q41D ABCD 0;Q42I ABCD 0;Q42V ABCD 0;Q42W ABCD 0;Q42S ABCD 0;Q42H ABCD 0;Q42C ABCD 0;Q42F ABCD 0;Q42D ABCD 0;Q43I ABCD 0;Q43V ABCD 0;Q43W ABCD 0;Q43S ABCD 0;Q43H ABCD 0;Q43C ABCD 0;Q43F ABCD 0;Q43D ABCD 0;Q44I ABCD 0;Q44V ABCD 0;Q44W ABCD 0;Q44S ABCD 0;Q44H ABCD 0;Q44C ABCD 0;Q44F ABCD 0;Q44D ABCD 0;Q45I ABCD 0;Q45V ABCD 0;Q45W ABCD 0;Q45S ABCD 0;Q45H ABCD 0;Q45C ABCD 0;Q45F ABCD 0;Q45D ABCD 0;Q46I ABCD 0;Q46V ABCD 0;Q46W ABCD 0;Q46S ABCD 0;Q46H ABCD 0;Q46C ABCD 0;Q46F ABCD 0;Q46D ABCD 0;Q47I ABCD 0;Q47V ABCD 0;Q47W ABCD 0;Q47S ABCD 0;Q47H ABCD 0;Q47C ABCD 0;Q47F ABCD 0;Q47D ABCD 0; Stop;}}

class C7Nav:Actor {
 Array<int> Walk;Array<double> Floor;bool Ready;
 Default {Radius 22;Height 56;MaxStepHeight 8;+NOGRAVITY +THRUACTORS +NOBLOCKMAP}
 States {Spawn:TNT1 A -1;Stop;}
 int Cell(Vector2 p){int x=int(floor((p.X+768)/16)),y=int(floor((p.Y+640)/16));return x<0||x>=142||y<0||y>=119?-1:y*142+x;}
 Vector2 Point(int i){return(-760+(i%142)*16,-632+(i/142)*16);}
 void Build(){Walk.Resize(16898);Floor.Resize(16898);
 for(int i=0;i<16898;i++){Vector2 p=Point(i);let sec=level.PointInSector(p);double z=sec.floorplane.ZatPoint(p);SetOrigin((p.X,p.Y,z),false);Floor[i]=z;Walk[i]=CheckMove(p,PCM_NOACTORS)?1:0;}
 Ready=true;Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY,"C7 NAV_READY radius=22 grid=16");}
 int Neighbor(int i,int j){int n=j==0?i-1:j==1?i+1:j==2?i-142:i+142;if(n<0||n>=16898||!Walk[n]||abs(Floor[n]-Floor[i])>8)return -1;if(j<2&&n/142!=i/142)return -1;return n;}
 int Nearest(Vector2 p){int best=-1;double distance=1e20;for(int i=0;i<Walk.Size();i++){if(!Walk[i])continue;double d=(Point(i)-p).LengthSquared();if(d<distance){distance=d;best=i;}}return best;}
 void Flood(int goal,Array<int> dist){dist.Resize(16898);for(int i=0;i<dist.Size();i++)dist[i]=-1;if(goal<0)return;Array<int> queue;queue.Push(goal);dist[goal]=0;int head=0;while(head<queue.Size()){int i=queue[head++];for(int j=0;j<4;j++){int n=Neighbor(i,j);if(n>=0&&dist[n]<0){dist[n]=dist[i]+1;queue.Push(n);}}}}
}
class C7Debris:Actor {
 int Kind,Quiet,Life,KickCooldown;bool Asleep;Vector3 Motion;
 Default {Radius 3;Height 4;Scale .2;+NOGRAVITY +NOBLOOD +THRUACTORS}
 States {Spawn:C7BK A -1;Stop;}
 override void Tick(){
  // Native horizontal movement and floor queries, v2 resting clamp, six quiet tics to sleep.
  Motion=Vel;Super.Tick();FCheckPosition contact;CheckPosition(Pos.XY,false,contact);double support=contact.floorz;Life++;if(KickCooldown>0)KickCooldown--;
  sprite=GetSpriteIndex(Kind==0?"C7BK":Kind==1?"C7RT":"C7LT");frame=0;
  let p=players[0].mo;if(p&&p.health>0&&KickCooldown==0&&Distance2D(p)<p.Radius+Radius+3&&abs(p.Pos.Z-Pos.Z)<24&&p.Vel.XY.Length()>.2){
   Vector2 kick=Pos.XY-p.Pos.XY;if(kick.Length()>.01)kick=kick.Unit();Vel.X=kick.X*1.3;Vel.Y=kick.Y*1.3;Vel.Z=1.1;Quiet=0;Asleep=false;KickCooldown=18;
   Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY,"C7 DEBRIS_KICK tic=%d",level.time);}
  bool rest=Pos.Z<=support+.01&&Vel.Z<=0;
  if(rest){SetOrigin((Pos.X,Pos.Y,support),false);double impact=-min(Motion.Z,Vel.Z);Vel.Z=impact>1.2?impact*.25:0;
   Vel.X*=.55;Vel.Y*=.55;if(impact>1.6)A_StartSound("c7/clatter",CHAN_BODY,0,clamp(impact*.08,.12,.45));}
  else {Asleep=false;Quiet=0;Vel.Z-=.8;}
  if(rest&&Vel.LengthSquared()<.04){Quiet++;if(Quiet>=6){Vel=(0,0,0);if(!Asleep)Console.PrintfEx(PRINT_LOG|PRINT_NONOTIFY,"C7 DEBRIS_SLEEP tic=%d age=%d z=%.2f floor=%.2f",level.time,Life,Pos.Z,support);Asleep=true;}}
  if(Asleep&&Pos.Z>support+.01){Asleep=false;Quiet=0;Vel.Z=-.8;}
 }
}
