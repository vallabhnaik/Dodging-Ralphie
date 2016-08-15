
from math import sin, cos
import sys
import time
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.gui.DirectGui import *
from panda3d.core import *
from direct.interval.IntervalGlobal import *
from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletHelper
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import BulletHeightfieldShape
from panda3d.bullet import BulletTriangleMesh
from panda3d.bullet import BulletTriangleMeshShape
from panda3d.bullet import BulletSoftBodyNode
from panda3d.bullet import BulletSoftBodyConfig
from panda3d.bullet import ZUp
from direct.task.TaskManagerGlobal import taskMgr
from threading import Thread

def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                        pos=(-1.3, pos), align=TextNode.ALeft, scale = .05)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1),
                        pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)


class CharacterController(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.keyMap = {"left":0, "right":0, "forward":0, "cam-left":0, "cam-right":0}
        self.count={"count":0}
        bk_text = "Dodging Ralphh"
        textObject = OnscreenText(text = bk_text, pos = (0.95,-0.95), 
        scale = 0.07,fg=(1,0.5,0.5,1),align=TextNode.ACenter,mayChange=1)
        self.setupLights()
        
        self.inst1 = addInstructions(0.95, "[ESC]: Quit")
        self.inst2 = addInstructions(0.90, "[Left Arrow]: Rotate Ralph Left")
        self.inst3 = addInstructions(0.85, "[Right Arrow]: Rotate Ralph Right")
        self.inst8 = addInstructions(0.80, "[Space]: Jump")
        self.inst4 = addInstructions(0.75, "[Up Arrow]: Run Ralph Forward")
        self.inst6 = addInstructions(0.70, "[A]: Rotate Camera Left")
        self.inst7 = addInstructions(0.65, "[S]: Rotate Camera Right")
        # Input
        self.accept('escape', self.doExit)
        self.accept('r', self.doReset)
        self.accept('f3', self.toggleDebug)
        self.accept('space', self.doJump)
        self.accept("escape", sys.exit)
        self.accept("arrow_left", self.setKey, ["left",1])
        self.accept("arrow_right", self.setKey, ["right",1])
        self.accept("arrow_up", self.setKey, ["forward",1])
        self.accept("a", self.setKey, ["cam-left",1])
        self.accept("s", self.setKey, ["cam-right",1])
        self.accept("arrow_left-up", self.setKey, ["left",0])
        self.accept("arrow_right-up", self.setKey, ["right",0])
        self.accept("arrow_up-up", self.setKey, ["forward",0])
        self.accept("a-up", self.setKey, ["cam-left",0])
        self.accept("s-up", self.setKey, ["cam-right",0])
        self.isMoving = False
        taskMgr.add(self.update, 'updateWorld')
        self.setup()
        base.setBackgroundColor(0, 0, 0, 1)
        base.setFrameRateMeter(True)
        base.disableMouse()
        self.voltage1.loop("walk")
        self.voltage1.loop("punch")
        self.voltage2.loop("walk")
        self.voltage2.loop("punch")
        self.voltage3.loop("walk")
        self.voltage3.loop("punch")
        self.voltage4.loop("walk")
        self.voltage4.loop("punch")

        
        # Create a frame
        frame = DirectFrame(text = "main", scale = 0.1, pos=(4,4,5))
        # Add button
        self.bar = DirectWaitBar(text = "", value = 100, range=100, pos = (0.6,0.6,0.8), scale = 0.5)
         
        mySound = base.loader.loadSfx("models/sound.mp3")
        mySound.play()
        #mySound.stop()
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)
        taskMgr.add(self.countCoins,'Count total Coins')
        
    def doExit(self):
        self.cleanup()
        sys.exit(1)

    def doReset(self):
        self.cleanup()
        self.setup()
    
    def incBar(self,arg):
        self.bar['value'] +=    arg
    
    def toggleDebug(self):
        if self.debugNP.isHidden():
            self.debugNP.show()
        else:
            self.debugNP.hide()

    def doJump(self):
        self.character.setMaxJumpHeight(12.5)
        self.character.setJumpSpeed(4.0)
        self.character.doJump()
        
    def setKey(self, key, value):
        self.keyMap[key] = value
    
    def update(self, task):
        dt = globalClock.getDt()
        #self.processInput(dt)
        #self.move(task)
        self.world.doPhysics(dt, 2, 1./50.)
        base.camera.lookAt(self.characterNP)
        if (self.keyMap["cam-left"]!=0):
            base.camera.setX(base.camera, - 20 * globalClock.getDt())
        if (self.keyMap["cam-right"]!=0):
            base.camera.setX(base.camera, + 20 * globalClock.getDt())
        
        startpos = self.characterNP.getPos() -10
        
        if (self.keyMap["left"]!=0):
            self.characterNP.setH(self.characterNP.getH() + 80 * globalClock.getDt())
        if (self.keyMap["right"]!=0):
            self.characterNP.setH(self.characterNP.getH() - 80 * globalClock.getDt())
        if (self.keyMap["forward"]!=0):
            self.characterNP.setY(self.characterNP, - 13 * globalClock.getDt())
            
        camvec = self.characterNP.getPos() - base.camera.getPos()
        camvec.setZ(-1)
        camdist = camvec.length() - 25
        camvec.normalize()
        if (camdist > 30.0):
            base.camera.setPos(base.camera.getPos() + camvec*(camdist-10))
            camdist = 30.0
        if (camdist < 20.0):
            base.camera.setPos(base.camera.getPos() - camvec*(5-camdist))
            camdist = 20.0

        # If characterNP is moving, loop the run animation.
        # If he is standing still, stop the animation.

        if (self.keyMap["forward"]!=0) or (self.keyMap["left"]!=0) or (self.keyMap["right"]!=0):
            if self.isMoving is False:
                self.actorNP.loop("walk")
                self.isMoving = True
        else:
            if self.isMoving:
                self.actorNP.stop()
                self.actorNP.pose("walk",5)
                self.voltage1.loop("walk", 5)
                self.isMoving = False


        # If the camera is too far from ralph, move it closer.
        # If the camera is too close to ralph, move it farther.
        
        
        self.floater.setPos(self.characterNP.getPos())
        self.floater.setZ(self.characterNP.getZ() + 10.0)
        base.camera.lookAt(self.actorNP)
        
        self.voltage1.lookAt(self.actorNP)
        #self.characterNP.reparentTo()
        
        ralphPos = self.actorNP.getPos()
        voltage1Pos = self.voltage1.getPos()
        distance = ralphPos-voltage1Pos
        distance.setZ(0)
        enemy1Distance = distance.length()
        if(enemy1Distance < 6):
            self.voltage1.lookAt(self.actorNP)
            self.voltage1.setH(self.voltage1.getH()-180)
            #self.voltage1.setPos(0,0,1)
            #DirectButton(text="-10",scale=0.05,pos=(0.6,.6,0), command=incBar,extraArgs = [-10])
        
        pickup_radius = 500
        for i in render.findAllMatches("**/=coin"):
            distance = self.characterNP.getDistance(i)
            print distance
            if (distance < pickup_radius):
                i.removeNode()
        
        zDistance = self.characterNP.getZ()
        if (zDistance <= 1):
            bk_text = "Game Over!! Press Escape to Exit"
            textObject = OnscreenText(text = bk_text, pos = (0.02,0.02), 
                                      scale = 0.2,fg=(1,0.5,0.5,1),align=TextNode.ACenter,mayChange=1)
        
        self.testAllContactingBodies()
        self.moveVoltage()
        return task.cont
                                      
    def testAllContactingBodies(self):
        # test for all the contacts in the bullet world
        manifolds = self.world.getManifolds() # returns a list of BulletPersistentManifold objects
        i=0
        for manifold in manifolds:    
                    
            print manifold.getNode0().getName(), " is in contact with ", manifold.getNode1().getName()        
            
            if manifold.getNode1().getName()=="collect0":
                print manifold.getNode0().getName(), " is in contact with ", manifold.getNode1().getName() 
                #BulletRigidBodyNode().remove_shape(self.shape1)
                #self.collectableNP.setCollideMask(BitMask32.allOff())
                self.actorNP+"0".removeNode()
                self.collectableNP.setCollideMask(BitMask32.allOff())
                i+=i
    
    
    def moveVoltage(self):
        ralphPos = self.characterNP.getPos()
        voltage1Pos = self.characterNP1.getPos()
        voltage2Pos = self.characterNP2.getPos()
        voltage3Pos = self.characterNP3.getPos()
        voltage4Pos = self.characterNP4.getPos()
        distance1 = ralphPos - voltage1Pos
        distance2 = ralphPos - voltage2Pos
        distance3 = ralphPos - voltage3Pos
        distance4 = ralphPos - voltage4Pos
        distance4.setZ(0)
        distance3.setZ(0)
        distance2.setZ(0)
        distance1.setZ(0)
        enemyDistance4 = distance4.length()
        enemyDistance3 = distance3.length()
        enemyDistance2 = distance2.length()
        enemyDistance1 = distance1.length()
        if(enemyDistance1 < 1):
            self.voltage1.loop("punch")
            voltageHprInterval1 = self.voltage1.hprInterval(3, Point3(270, 0, 0),
                                                        startHpr=distance1)
            self.pandasPace = Sequence(voltageHprInterval1,
                                  name="pandasPace")

            self.actorNP.setPos(self.voltage1.getPos() - enemyDistance1)
            actor = self.characterNP.getPos()
            evil = self.characterNP1.getPos()
            distance1 = actor - evil
            enemyDist8 = distance1.length()
            self.characterNP.setPos(self.characterNP.getPos()-enemyDist8 + 5)
            self.actorNP.setPos(0,0,-1)
            #smooth fall
            i=0
            while(i<10):
                self.characterNP1.setX(self.characterNP1.getX() - 0.5)
                base.graphicsEngine.renderFrame()
                self.voltage1.setPos(0,0,0)
                time.sleep(0.0000001)
                i+=1
            self.incBar(-20)
        elif(enemyDistance2 < 1):
            self.voltage2.loop("punch")
            voltageHprInterval2 = self.voltage2.hprInterval(3, Point3(270, 0, 0),
                                                        startHpr=distance2)
            self.pandasPace = Sequence(voltageHprInterval2,
                                  name="pandasPace")

            self.actorNP.setPos(self.voltage2.getPos() - enemyDistance2)
            actor = self.characterNP.getPos()
            evil = self.characterNP2.getPos()
            distance2 = actor - evil
            enemyDist8 = distance2.length()
            self.characterNP.setPos(self.characterNP.getPos()-enemyDist8 + 5)
            self.actorNP.setPos(0,0,-1)
            #smooth fall
            i=0
            while(i<10):
                self.characterNP2.setX(self.characterNP2.getX() - 0.5)
                base.graphicsEngine.renderFrame()
                self.voltage2.setPos(0,0,0)
                time.sleep(0.0000001)
                i+=1
            self.incBar(-20)
        elif(enemyDistance3 < 1):
            self.voltage3.loop("punch")
            voltageHprInterval3 = self.voltage3.hprInterval(3, Point3(270, 0, 0),
                                                        startHpr=distance3)
            self.pandasPace = Sequence(voltageHprInterval3,
                                  name="pandasPace")

            self.actorNP.setPos(self.voltage3.getPos() - enemyDistance3)
            actor = self.characterNP.getPos()
            evil = self.characterNP3.getPos()
            distance3 = actor - evil
            enemyDist8 = distance3.length()
            self.characterNP.setPos(self.characterNP.getPos()-enemyDist8 + 5)
            self.actorNP.setPos(0,0,-1)
            #smooth fall
            i=0
            while(i<10):
                self.characterNP3.setX(self.characterNP3.getX() - 0.5)
                base.graphicsEngine.renderFrame()
                self.voltage3.setPos(0,0,0)
                time.sleep(0.0000001)
                i+=1
            self.incBar(-20)
        elif(enemyDistance4 < 1):
            self.voltage4.loop("punch")
            voltageHprInterval4 = self.voltage4.hprInterval(3, Point3(270, 0, 0),
                                                        startHpr=distance4)
            self.pandasPace = Sequence(voltageHprInterval4,
                                  name="pandasPace")

            self.actorNP.setPos(self.voltage4.getPos() - enemyDistance4)
            actor = self.characterNP.getPos()
            evil = self.characterNP4.getPos()
            distance4 = actor - evil
            enemyDist8 = distance4.length()
            self.characterNP.setPos(self.characterNP.getPos()-enemyDist8 + 5)
            self.actorNP.setPos(0,0,-1)
            #smooth fall
            i=0
            while(i<10):
                self.characterNP4.setX(self.characterNP4.getX() - 0.5)
                base.graphicsEngine.renderFrame()
                self.voltage4.setPos(0,0,0)
                time.sleep(0.0000001)
                i+=1
            self.incBar(-20)
            
    def itemSel(arg):
        if(arg):
            output = "Button Selected is: Yes"
        else:
            output = "Button Selected is: No"
            textObject.setText(output)
     
    
    def cleanup(self):
        self.world = None
        self.render.removeNode()

    def setupLights(self):
        # Light
        alight = AmbientLight('ambientLight')
        alight.setColor(Vec4(0.5, 0.5, 0.5, 1))
        alightNP = render.attachNewNode(alight)

        dlight = DirectionalLight('directionalLight')
        dlight.setDirection(Vec3(1, 1, -1))
        dlight.setColor(Vec4(0.7, 0.7, 0.7, 1))
        dlightNP = render.attachNewNode(dlight)

        self.render.clearLight()
        self.render.setLight(alightNP)
        self.render.setLight(dlightNP)
    
    def countCoins(self, task):
        print "collected coins"+str("no_of_Coin")
        
    
    def setup(self):
        
        # World
        self.debugNP = self.render.attachNewNode(BulletDebugNode('Debug'))
        self.debugNP.show()

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        #self.world.setDebugNode(self.debugNP.node())
        self.background = OnscreenImage(parent=render2dp, image= "models/nature.jpg")
        base.cam2dp.node().getDisplayRegion(0).setSort(-100)
        # Floor
        shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        floorNP = self.render.attachNewNode(BulletRigidBodyNode('Floor'))
        floorNP.node().addShape(shape)
        floorNP.setPos(0, 0, 0)
        floorNP.setCollideMask(BitMask32.allOn())
        self.world.attachRigidBody(floorNP.node())

        # Plank 1
        origin = Point3(2, 0, 0)
        size = Vec3(1, 2, 1)
        shape = BulletBoxShape(Vec3(5,3,1))
        floorNode = BulletRigidBodyNode('Plank1')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(1,0,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(10,6,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        
        # Plank 2
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(5,3,1))
        floorNode = BulletRigidBodyNode('Plank2')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(1,0,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(10,6,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        PosInterval1 = floorNodePath.posInterval(10, Point3(1, -10 , 1),
        startPos=Point3(1, -18, 1))
        PosInterval2 = floorNodePath.posInterval(10, Point3(1, -18, 1),
        startPos=Point3(1, -10, 1))
        self.movingPlanks = Sequence(PosInterval1, PosInterval2, name="Plank2")
        self.movingPlanks.loop()
        
        
        # Plank 3
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(5,3,1))
        floorNode = BulletRigidBodyNode('Plank3')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(1,-26,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(10,6,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        PosInterval1 = floorNodePath.posInterval(7, Point3(1, -32 , 1),
        startPos=Point3(1, -26, 1))
        PosInterval2 = floorNodePath.posInterval(7, Point3(1, -26, 1),
        startPos=Point3(1, -32, 1))
        self.movingPlanks = Sequence(PosInterval1, PosInterval2, name="Plank3")
        self.movingPlanks.loop()
        for i in range(1):
            coinModel = self.loader.loadModel('models/emerald.egg')
            coinModel.reparentTo(self.render)
            coinModel.setPos(1,-22,5)
            coinModel.setScale(0.007)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex,1)
            coinModel.setHpr(0,0,-20)
            coinModel.setTag("coin",str(i))
            
        # Plank 4
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(5,9,1))
        floorNode = BulletRigidBodyNode('Plank4')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(1,-48,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(10,18,1)
        floorModel.setPos(0,0,0)
        floorModel.setColor(0,0,0)
        floorModel.reparentTo(floorNodePath)
        for i in range(1):
            coinModel = self.loader.loadModel('models/emerald.egg')
            coinModel.reparentTo(self.render)
            coinModel.setPos(1,-42,5)
            coinModel.setScale(0.007)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex,1)
            coinModel.setHpr(0,0,-20)
            coinModel.setTag("coin",str(i))
        for i in range(1):
            coinModel = self.loader.loadModel('models/emerald.egg')
            coinModel.reparentTo(self.render)
            coinModel.setPos(1,-50,5)
            coinModel.setScale(0.007)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex,1)
            coinModel.setHpr(0,0,-20)
            coinModel.setTag("coin",str(i))
        
        # Plank 5
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(5,3,1))
        floorNode = BulletRigidBodyNode('Plank5')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(1,-64,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(10,6,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        PosInterval1 = floorNodePath.posInterval(10, Point3(1, -64 , 6),
        startPos=Point3(1, -64, 0))
        PosInterval2 = floorNodePath.posInterval(10, Point3(1, -64, 0),
        startPos=Point3(1, -64, 6))
        self.movingPlanks = Sequence(PosInterval1, PosInterval2, name="Plank5")
        self.movingPlanks.loop()
        
        # Plank 6
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(5,12,1))
        floorNode = BulletRigidBodyNode('Plank6')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(1,-84,4)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(10,24,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        for i in range(1):
            coinModel = self.loader.loadModel('models/emerald.egg')
            coinModel.reparentTo(self.render)
            coinModel.setPos(1,-84,7)
            coinModel.setScale(0.007)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex,1)
            coinModel.setHpr(0,0,-20)
            coinModel.setTag("coin",str(i))
        
        # Plank 7
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(5,3,1))
        floorNode = BulletRigidBodyNode('Plank7')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(1,-104,4)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(10,6,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        PosInterval1 = floorNodePath.posInterval(7, Point3(1, -104 , 4),
        startPos=Point3(1, -104, 0))
        PosInterval2 = floorNodePath.posInterval(7, Point3(1, -104, 0),
        startPos=Point3(1, -104, 4))
        self.movingPlanks = Sequence(PosInterval1, PosInterval2, name="Plank7")
        self.movingPlanks.loop()
        
        # Plank 8
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(5,3,1))
        floorNode = BulletRigidBodyNode('Plank8')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(1,-114,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(10,6,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        for i in range(1):
            coinModel = self.loader.loadModel('models/emerald.egg')
            coinModel.reparentTo(self.render)
            coinModel.setPos(1,-114,5)
            coinModel.setScale(0.007)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex,1)
            coinModel.setHpr(0,0,-20)
            coinModel.setTag("coin",str(i))
        
        # Plank 9
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(5,6,1))
        floorNode = BulletRigidBodyNode('Plank9')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(1,-130,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(10,12,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        for i in range(1):
            coinModel = self.loader.loadModel('models/emerald.egg')
            coinModel.reparentTo(self.render)
            coinModel.setPos(1,-130,5)
            coinModel.setScale(0.007)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex,1)
            coinModel.setHpr(0,0,-20)
            coinModel.setTag("coin",str(i))
                
        # Plank 10
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(5,3,1))
        floorNode = BulletRigidBodyNode('Plank11')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(1,-144,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(10,6,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        for i in range(1):
            coinModel = self.loader.loadModel('models/emerald.egg')
            coinModel.reparentTo(self.render)
            coinModel.setPos(1,-144,4)
            coinModel.setScale(0.007)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex,1)
            coinModel.setHpr(0,0,-20)
            coinModel.setTag("coin",str(i))
        
        # Plank 11
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(5,3,1))
        floorNode = BulletRigidBodyNode('Plank11')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(1,-154,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(10,6,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        PosInterval1 = floorNodePath.posInterval(7, Point3(-5, -154 , 2),
        startPos=Point3(5, -154, 2))
        PosInterval2 = floorNodePath.posInterval(7, Point3(5, -154, 2),
        startPos=Point3(-5, -154, 2))
        self.movingPlanks = Sequence(PosInterval1, PosInterval2, name="Plank11")
        self.movingPlanks.loop()
        
        # Plank 12
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(10,3,1))
        floorNode = BulletRigidBodyNode('Plank12')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(20,-154,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(20,6,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        for i in range(1):
            coinModel = self.loader.loadModel('models/emerald.egg')
            coinModel.reparentTo(self.render)
            coinModel.setPos(20,-154,5)
            coinModel.setScale(0.007)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex,1)
            coinModel.setHpr(0,0,-20)
            coinModel.setTag("coin",str(i))
        
          
        # Plank 13
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(3,5,1))
        floorNode = BulletRigidBodyNode('Plank13')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(40,-158,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(6,10,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        for i in range(1):
            coinModel = self.loader.loadModel('models/emerald.egg')
            coinModel.reparentTo(self.render)
            coinModel.setPos(40,-158,5)
            coinModel.setScale(0.007)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex,1)
            coinModel.setHpr(0,0,-20)
            coinModel.setTag("coin",str(i))
            
        # Plank 14
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(10,3,1))
        floorNode = BulletRigidBodyNode('Plank14')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-20,-154,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(20,6,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        for i in range(1):
            coinModel = self.loader.loadModel('models/emerald.egg')
            coinModel.reparentTo(self.render)
            coinModel.setPos(-20,-154,5)
            coinModel.setScale(0.007)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex,1)
            coinModel.setHpr(0,0,-20)
            coinModel.setTag("coin",str(i))
        
        # Plank 15
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(3,5,1))
        floorNode = BulletRigidBodyNode('Plank15')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-40,-158,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(6,10,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        for i in range(1):
            coinModel = self.loader.loadModel('models/emerald.egg')
            coinModel.reparentTo(self.render)
            coinModel.setPos(-40,-158,5)
            coinModel.setScale(0.007)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex,1)
            coinModel.setHpr(0,0,-20)
            coinModel.setTag("coin",str(i))
        
        # Plank 16
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(3,10,1))
        floorNode = BulletRigidBodyNode('Plank16')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-40,-180,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(6,20,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        for i in range(1):
            coinModel = self.loader.loadModel('models/emerald.egg')
            coinModel.reparentTo(self.render)
            coinModel.setPos(-40,-180,5)
            coinModel.setScale(0.007)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex,1)
            coinModel.setHpr(0,0,-20)
            coinModel.setTag("coin",str(i))
        
        # Plank 17
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(3,10,1))
        floorNode = BulletRigidBodyNode('Plank17')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(40,-180,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(6,20,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        for i in range(1):
            coinModel = self.loader.loadModel('models/emerald.egg')
            coinModel.reparentTo(self.render)
            coinModel.setPos(40,-180,5)
            coinModel.setScale(0.007)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex,1)
            coinModel.setHpr(0,0,-20)
            coinModel.setTag("coin",str(i))
        
        # Plank 18
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(3,5,1))
        floorNode = BulletRigidBodyNode('Plank18')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-40,-200,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(6,10,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        for i in range(1):
            coinModel = self.loader.loadModel('models/emerald.egg')
            coinModel.reparentTo(self.render)
            coinModel.setPos(-40,-200,5)
            coinModel.setScale(0.007)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex,1)
            coinModel.setHpr(0,0,-20)
            coinModel.setTag("coin",str(i))
        
        # Plank 19
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(3,5,1))
        floorNode = BulletRigidBodyNode('Plank19')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(40,-200,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(6,10,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        for i in range(1):
            coinModel = self.loader.loadModel('models/emerald.egg')
            coinModel.reparentTo(self.render)
            coinModel.setPos(40,-200,5)
            coinModel.setScale(0.007)
            coin_tex = self.loader.loadTexture("models/coin-texture.jpg")
            coinModel.setTexture(coin_tex,1)
            coinModel.setHpr(0,0,-20)
            coinModel.setTag("coin",str(i))
        
        # Plank 20
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(5,3,1))
        floorNode = BulletRigidBodyNode('Plank20')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(-40,-210,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(10,6,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        PosInterval1 = floorNodePath.posInterval(8, Point3(-15, -210 , 2),
        startPos=Point3(-40, -210, 2))
        PosInterval2 = floorNodePath.posInterval(8, Point3(-40, -210, 2),
        startPos=Point3(-15, -210, 2))
        self.movingPlanks = Sequence(PosInterval1, PosInterval2, name="Plank20")
        self.movingPlanks.loop()
        
        # Plank 21
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(5,3,1))
        floorNode = BulletRigidBodyNode('Plank21')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(40,-210,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(10,6,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        PosInterval1 = floorNodePath.posInterval(7, Point3(15, -210 , 2),
        startPos=Point3(40, -210, 2))
        PosInterval2 = floorNodePath.posInterval(7, Point3(40, -210, 2),
        startPos=Point3(15, -210, 2))
        self.movingPlanks = Sequence(PosInterval1, PosInterval2, name="Plank21")
        self.movingPlanks.loop()
        
        # Plank 22
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(5,3,1))
        floorNode = BulletRigidBodyNode('Plank22')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(1,-210,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(10,6,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        
        
        # Plank 23
        origin = Point3(2, 0, 0)
        size = Vec3(2, 2, 2)
        shape = BulletBoxShape(Vec3(5,6,1))
        floorNode = BulletRigidBodyNode('Plank23')
        floorNode.addShape(shape)
        floorNodePath = self.render.attachNewNode(floorNode)
        floorNodePath.setCollideMask(BitMask32.allOn())
        floorNodePath.setPos(1,-224,2)
        self.world.attachRigidBody(floorNodePath.node())
        floorModel = self.loader.loadModel("models/stone.egg")
        floorModel.setScale(10,12,1)
        floorModel.setPos(0,0,0)
        floorModel.reparentTo(floorNodePath)
        #####################################################################################################        
        # Character - Ralph
        h = 1.75
        w = 0.4
        shape = BulletCapsuleShape(w, h - 2 * w, ZUp)

        self.character = BulletCharacterControllerNode(shape, 0.4, 'Player')
        self.characterNP = self.render.attachNewNode(self.character)
        self.characterNP.setPos(1, 0, 10)
        self.characterNP.setH(45)
        self.characterNP.setCollideMask(BitMask32.allOn())
        self.world.attachCharacter(self.character)

        self.actorNP = Actor('models/ralph.egg', {
                         'run' : 'models/ralph-run.egg',
                         'walk' : 'models/ralph-walk.egg',
                         'jump' : 'models/ralph-jump.egg'})

        self.actorNP.reparentTo(self.characterNP)
        self.actorNP.setScale(0.4000)
        self.actorNP.setH(0)
        self.actorNP.setPos(0, 0, -1)
        
        # Character - Security Guard 2
        h = 1.75
        w = 0.4
        shape = BulletCapsuleShape(w, h - 2 * w, ZUp)

        self.character2 = BulletCharacterControllerNode(shape, 0.4, 'voltage1')
        #    self.character.setMass(1.0)
        self.characterNP1 = self.render.attachNewNode(self.character2)
        self.characterNP1.setPos(1, -48, 6)
        self.characterNP1.setH(180)
        self.characterNP1.setCollideMask(BitMask32.allOn())
        self.world.attachCharacter(self.character2)

        self.voltage1 = Actor('models/Bricker3.egg', {
                         'walk' : 'models/Bricker-walk.egg',
                         'run' : 'models/Bricker-run.egg',
                         'jump' : 'models/Bricker-jump.egg',
                         'punch' : 'models/Bricker-punch.egg',
                         'superpunch' :'models/Bricker-superpunch'})

        self.voltage1.reparentTo(self.characterNP1)
        self.voltage1.setScale(0.3060)
        self.voltage1.setH(180)
        self.voltage1.setPos(0, 0, 0)
        
        
        # Character - Security Guard 3
        h = 1.75
        w = 0.4
        shape = BulletCapsuleShape(w, h - 2 * w, ZUp)

        self.character3 = BulletCharacterControllerNode(shape, 0.4, 'voltage2')
        self.characterNP2 = self.render.attachNewNode(self.character3)
        self.characterNP2.setPos(1, -84, 8)
        self.characterNP2.setH(180)
        self.characterNP2.setCollideMask(BitMask32.allOn())
        self.world.attachCharacter(self.character3)

        self.voltage2 = Actor('models/Bricker3.egg', {
                         'walk' : 'models/Bricker-walk.egg',
                         'run' : 'models/Bricker-run.egg',
                         'jump' : 'models/Bricker-jump.egg',
                         'punch' : 'models/Bricker-punch.egg',
                         'superpunch' :'models/Bricker-superpunch'})

        self.voltage2.reparentTo(self.characterNP2)
        self.voltage2.setScale(0.3060)
        self.voltage2.setH(180)
        self.voltage2.setPos(0, 0, 0)
        
        # Character - Security Guard 3
        h = 1.75
        w = 0.4
        shape = BulletCapsuleShape(w, h - 2 * w, ZUp)

        self.character4 = BulletCharacterControllerNode(shape, 0.4, 'voltage3')
        self.characterNP3 = self.render.attachNewNode(self.character4)
        self.characterNP3.setPos(40,-180,6)
        self.characterNP3.setH(180)
        self.characterNP3.setCollideMask(BitMask32.allOn())
        self.world.attachCharacter(self.character4)

        self.voltage3 = Actor('models/Bricker3.egg', {
                         'walk' : 'models/Bricker-walk.egg',
                         'run' : 'models/Bricker-run.egg',
                         'jump' : 'models/Bricker-jump.egg',
                         'punch' : 'models/Bricker-punch.egg',
                         'superpunch' :'models/Bricker-superpunch'})

        self.voltage3.reparentTo(self.characterNP3)
        self.voltage3.setScale(0.3060)
        self.voltage3.setH(180)
        self.voltage3.setPos(0, 0, 0)
        
        # Character - Security Guard 4
        h = 1.75
        w = 0.4
        shape = BulletCapsuleShape(w, h - 2 * w, ZUp)

        self.character5 = BulletCharacterControllerNode(shape, 0.4, 'voltage4')
        self.characterNP4 = self.render.attachNewNode(self.character5)
        self.characterNP4.setPos(-40,-180,6)
        self.characterNP4.setH(180)
        self.characterNP4.setCollideMask(BitMask32.allOn())
        self.world.attachCharacter(self.character5)

        self.voltage4 = Actor('models/Bricker3.egg', {
                         'walk' : 'models/Bricker-walk.egg',
                         'run' : 'models/Bricker-run.egg',
                         'jump' : 'models/Bricker-jump.egg',
                         'punch' : 'models/Bricker-punch.egg',
                         'superpunch' :'models/Bricker-superpunch'})

        self.voltage4.reparentTo(self.characterNP4)
        self.voltage4.setScale(0.3060)
        self.voltage4.setH(180)
        self.voltage4.setPos(0, 0, 0)
        
game = CharacterController()
game.run()
