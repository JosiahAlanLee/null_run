class NRGlyphDot : Actor {
 Default { Radius 1; Height 1; Scale 1; RenderStyle "Add"; +NOGRAVITY +NOINTERACTION +BRIGHT +ROLLSPRITE +FORCEXYBILLBOARD +BILLBOARDNOFACECAMERA }
 States { Spawn: NSGD A -1 Bright; Stop; }
}
class NRGlyphPen : NRGlyphDot {
 Default { Scale .6; }
 States { Spawn: NSGP A -1 Bright; Stop; }
}
class NRGlyphLight : PointLight {
 Default { Args 238,170,72,96; }
}
class NRSigilCaster : Actor {
 int Phase,Age,Clock,TotalFires,Interrupts,ShotCount,Visible,PeakUpdates,Updates,BoundaryDamage;
 int BrokenAt,Glyph;
 NRGlyphDot Dots[32]; NRGlyphLight Lamp; NRGlyphPen Pen;
 Default { Health 10000; Radius 20; Height 56; +SHOOTABLE +NOGRAVITY +SOLID }
 States { Spawn: POSS A -1; Stop; Death: POSS H -1; Stop; }
 void ClearInk() {
  for(int i=0;i<32;i++) {if(Dots[i]){Dots[i].Destroy();Dots[i]=null;}}
  if(Lamp){Lamp.Destroy();Lamp=null;} if(Pen){Pen.Destroy();Pen=null;} Visible=0;
 }
 override void OnDestroy(){ClearInk();Super.OnDestroy();}
 void StartCast(){ClearInk();Phase=1;Age=0;BrokenAt=0;
  for(int i=0;i<32;i++){Dots[i]=NRGlyphDot(Actor.Spawn('NRGlyphDot',Pos));Dots[i].bINVISIBLE=true;}
  Lamp=NRGlyphLight(Actor.Spawn('NRGlyphLight',Pos+(0,0,100))); Pen=NRGlyphPen(Actor.Spawn('NRGlyphPen',Pos));
 }
 void BreakCast(){if(Phase!=1 && Phase!=4)return;BrokenAt=Age;Phase=2;Age=0;Interrupts++;}
 override int DamageMobj(Actor inflictor,Actor source,int damage,Name mod,int flags,double angle){
  int result=Super.DamageMobj(inflictor,source,damage,mod,flags,angle);
  if(result>0){if(health<=0){ClearInk();Phase=5;}else BreakCast();}return result;
 }
 void Volley(int count){
  for(int j=0;j<count;j++){
   let ball=Actor.Spawn('DoomImpBall',Pos+(0,-28,40));if(ball){ball.target=self;double a=count==1?270:360.*j/count;ball.Vel=(cos(a)*9,sin(a)*9,0);ShotCount++;}
  }
 }
 Vector3 InkPosition(Vector2 q) {
  // This private single-player prototype faces its entire glyph plane to player 0.
  let p=players[0].mo;double a=p.Angle, pitch=p.Pitch;
  Vector3 right=(sin(a),-cos(a),0);
  Vector3 up=(sin(pitch)*cos(a),sin(pitch)*sin(a),cos(pitch));
  return Pos+(0,16,96)+right*((q.X-.5)*128)+up*((.5-q.Y)*128);
 }
 void DrawInk(){
  Visible=0;Updates=0;
  int t=Phase==2?BrokenAt:Min(Age,NRGlyphData.Total());
  double fade=Phase==2?Max(0,1.-Age/24.):Phase==3?Max(0,1.-Age/10.):1.;
  for(int i=0;i<32;i++){
   Vector2 q=NRGlyphData.Point(Glyph,t,i*2,Phase==2);
   Vector2 v=NRGlyphData.Point(Glyph,t,i*2+1,Phase==2);Updates++;
   if(Dots[i]){
    Dots[i].bINVISIBLE=q.X<0;
    if(q.X>=0){
     Visible++;Vector3 center=InkPosition((q+v)*.5);
     if(Phase==2){center.Z-=Age*Age*.10;center.X+=sin(i*67)*Age*.35;}
     Dots[i].SetOrigin(center,false);
     Dots[i].Scale=((v-q).Length()*128/64.+.025,.625);
     Dots[i].roll=atan2(q.Y-v.Y,v.X-q.X);
     Dots[i].Alpha=fade;Dots[i].frame=Phase==2?1:0;
    }
   }
  }
  PeakUpdates=Max(PeakUpdates,Updates);
  Vector2 tip=NRGlyphData.Point(Glyph,t,192,false);Vector3 penpos=InkPosition(tip);
  if(Pen){Pen.SetOrigin(penpos,false);Pen.Alpha=fade;Pen.bINVISIBLE=Phase==3;}
  if(Lamp){Lamp.SetOrigin(penpos,false);Lamp.args[3]=Phase==2?(Max(0,96-Age*6)):Phase==3?Max(0,96-Age*10):96;}
 }
 override void Tick(){
  Super.Tick();Clock++;Updates=0;
  if(health<=0){ClearInk();Phase=5;return;}
  if(Phase==0)return;
  if(Phase==1 || Phase==4){
   // Preserve the placed caster position in this integration fixture.
   if(Phase==4){let fx=NREngineFX(StaticEventHandler.Find('NREngineFX'));if(fx)fx.SigilCompleted();TotalFires++;Volley(8);Phase=3;Age=0;return;}
   Age++;if(Age%21==0)Volley(1);DrawInk();
   if(Age>=NRGlyphData.Total())Phase=4;
   // Actor-side injection proves damage BEFORE event-handler completion-boundary damage.
   if(BoundaryDamage==1 && Phase==4){BoundaryDamage=0;DamageMobj(null,null,1,'Probe');}
  }else if(Phase==2){Age++;DrawInk();if(Age>=24){ClearInk();Phase=3;Age=0;}}
  else if(Phase==3){Age++;if(Age<10)DrawInk();if(Age==10)ClearInk();if(Age>=35){Phase=0;Age=0;}}
 }
}
