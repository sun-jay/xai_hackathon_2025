"use client";

import { Effects } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { Particles } from "./particles";
import { VignetteShader } from "./shaders/vignetteShader";

export const GL = ({ hovering = false }: { hovering?: boolean }) => {
  return (
    <div id="webgl">
      <Canvas
        camera={{
          position: [1.26, 2.66, -1.82],
          fov: 50,
          near: 0.01,
          far: 300,
        }}
      >
        <color attach="background" args={["#000"]} />
        <Particles introspect={hovering} />
        <Effects multisamping={0} disableGamma>
          <shaderPass
            args={[VignetteShader]}
            uniforms-darkness-value={1.5}
            uniforms-offset-value={0.4}
          />
        </Effects>
      </Canvas>
    </div>
  );
};

