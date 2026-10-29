"""Deterministic real MuJoCo CPU physics step, no graphical renderer."""
import math
import mujoco

xml='''<mujoco model="imandrax_pendulum"><option timestep="0.002" gravity="0 0 -9.81"/>
<worldbody><body name="pendulum" pos="0 0 1"><joint name="hinge" type="hinge" axis="0 1 0"/>
<geom type="capsule" fromto="0 0 0 0 0 -0.6" size="0.04" density="1000"/></body></worldbody>
</mujoco>'''
model=mujoco.MjModel.from_xml_string(xml)
assert model.nq==1 and model.nv==1
results=[]
for _ in range(2):
    data=mujoco.MjData(model)
    data.qpos[0]=0.5
    for step in range(200):
        mujoco.mj_step(model,data)
    results.append((float(data.qpos[0]),float(data.qvel[0])))
assert all(math.isfinite(x) for state in results for x in state)
assert all(abs(a-b)<1e-12 for a,b in zip(results[0],results[1]))
assert abs(results[0][0]-0.5)>0.01
print({'mujoco_version':mujoco.__version__,'steps':200,'repeatable':True,'qpos':results[0][0]})