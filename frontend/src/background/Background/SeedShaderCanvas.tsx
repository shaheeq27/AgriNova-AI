'use client';

import React, { useEffect, useRef } from 'react';

export interface SeedShaderCanvasProps {
  isWelcomeMode?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

export function SeedShaderCanvas({ className, style, isWelcomeMode = false }: SeedShaderCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    let animFrameId: number;

    function syncSize() {
      if (!canvas) return;
      const w = canvas.clientWidth || window.innerWidth;
      const h = canvas.clientHeight || window.innerHeight;
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
      }
    }

    const resizeObserver =
      typeof ResizeObserver !== 'undefined'
        ? new ResizeObserver(syncSize)
        : null;

    if (resizeObserver) {
      resizeObserver.observe(canvas);
    }
    syncSize();

    const gl = (canvas.getContext('webgl') ||
      canvas.getContext('experimental-webgl')) as WebGLRenderingContext | null;
    if (!gl) return;

    const vs = `attribute vec2 a_position;
varying vec2 v_texCoord;
void main() {
  v_texCoord = a_position * 0.5 + 0.5;
  gl_Position = vec4(a_position, 0.0, 1.0);
}`;

    const fs = `precision highp float;
uniform float u_time;
uniform vec2 u_resolution;
uniform float u_reduced_motion;
uniform float u_welcome_mode;
varying vec2 v_texCoord;

// High quality pseudo-random hash
float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

void main() {
    vec2 uv = v_texCoord;
    float aspect = u_resolution.x / u_resolution.y;
    vec2 st = vec2(uv.x * aspect, uv.y);

    // Very Dark Forest Green Background #030A04
    vec3 backgroundColor = vec3(0.011, 0.039, 0.015);
    vec3 color = backgroundColor;

    // Neon Mint Seed Color #ADFF00
    vec3 seedColor = vec3(0.678, 1.0, 0.0);

    if (u_reduced_motion > 0.5) {
        float n = hash(uv * 10.0);
        color += seedColor * n * 0.02;
        gl_FragColor = vec4(color, 1.0);
        return;
    }

    for(float i = 0.0; i < 65.0; i++) {
        float h1 = hash(vec2(i * 1.31, 123.456));
        float h2 = hash(vec2(i * 2.73, 789.012));
        float h3 = hash(vec2(i * 4.19, 345.678));

        if (u_welcome_mode > 0.5) {
            float speedPx = 150.0 + hash(vec2(i, 0.1)) * 130.0; // 150 to 280 px/sec
            float speedUV = speedPx / u_resolution.y;
            float travelUV = 1.20; // travel from y=-0.10 to y=1.10
            float travelTime = travelUV / speedUV;

            // Global 6-second block grid
            float blockDuration = 6.0;
            float cycleIndex = floor(u_time / blockDuration);
            float spawnDelay = hash(vec2(i, cycleIndex)) * 3.5; // Stagger 0-3.5s

            float spawnEventTime = cycleIndex * blockDuration + spawnDelay;
            float activeTime = u_time - spawnEventTime;

            // If hasn't spawned in current block, check previous block
            if (activeTime < 0.0) {
                cycleIndex -= 1.0;
                spawnDelay = hash(vec2(i, cycleIndex)) * 3.5;
                spawnEventTime = cycleIndex * blockDuration + spawnDelay;
                activeTime = u_time - spawnEventTime;
            }

            // Guarantee empty start at t=0
            if (cycleIndex < 0.0) {
                activeTime = -1.0;
            }

            if (activeTime >= 0.0 && activeTime < travelTime) {
                float progress = activeTime / travelTime;

                // Spawn strictly from the bottom
                float yPos = -0.10 + progress * travelUV;

                // Completely random independent values for this specific spawn cycle
                float spawnX = hash(vec2(i, cycleIndex + 10.0));
                float velocityXPx = -70.0 + hash(vec2(i, cycleIndex + 20.0)) * 140.0;
                float velocityXUV = velocityXPx / u_resolution.x;

                float xPos = spawnX + velocityXUV * activeTime;

                // Organic drift curve
                float curve = sin(progress * 3.14159) * (0.01 + hash(vec2(i, cycleIndex + 30.0)) * 0.03);
                xPos += curve;

                vec2 seedPosUV = vec2(xPos, yPos);
                vec2 seedPosST = vec2(seedPosUV.x * aspect, seedPosUV.y);
                float dist = length(st - seedPosST);

                float coreRadius = 0.0035 + hash(vec2(i, cycleIndex + 40.0)) * 0.0035;

                float fadeIn = smoothstep(0.0, 0.10, progress);
                float fadeOut = 1.0 - smoothstep(0.90, 1.0, progress);
                float opacity = fadeIn * fadeOut;

                float glow = coreRadius / (dist + 0.00001);
                glow = pow(glow, 1.25);

                float brightness = 0.45 + hash(vec2(i, cycleIndex + 50.0)) * 0.55;

                color += seedColor * (glow * 0.40) * brightness * opacity * 0.8;
            }
        } else {
            float baseX = h1;
            float speed = 0.03 + h2 * 0.07;
            float yPos = fract(u_time * speed + h3);
            float drift = sin(u_time * (0.5 + h2 * 1.0) + h1 * 6.2831) * (0.02 + h3 * 0.03);
            float xPos = baseX + drift;
            vec2 seedPosUV = vec2(xPos, yPos);
            vec2 seedPosST = vec2(seedPosUV.x * aspect, seedPosUV.y);
            float dist = length(st - seedPosST);
            float coreRadius = 0.0018 + h1 * 0.0022;
            float glow = coreRadius / (dist + 0.00001);
            glow = pow(glow, 1.25);
            float tailLength = 0.06 + h2 * 0.05;
            float tail = smoothstep(0.035, 0.0, dist) * smoothstep(seedPosUV.y, seedPosUV.y - tailLength, uv.y);
            float brightness = 0.45 + h3 * 0.55;
            color += seedColor * (glow * 0.40 + tail * 0.18) * brightness;
        }
    }

    gl_FragColor = vec4(color, 1.0);
}`;

    function createShader(type: number, src: string) {
      if (!gl) return null;
      const s = gl.createShader(type);
      if (!s) return null;
      gl.shaderSource(s, src);
      gl.compileShader(s);
      return s;
    }

    const vertShader = createShader(gl.VERTEX_SHADER, vs);
    const fragShader = createShader(gl.FRAGMENT_SHADER, fs);
    if (!vertShader || !fragShader) return;

    const prog = gl.createProgram();
    if (!prog) return;
    gl.attachShader(prog, vertShader);
    gl.attachShader(prog, fragShader);
    gl.linkProgram(prog);
    gl.useProgram(prog);

    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(
      gl.ARRAY_BUFFER,
      new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]),
      gl.STATIC_DRAW
    );

    const pos = gl.getAttribLocation(prog, 'a_position');
    if (pos >= 0) {
      gl.enableVertexAttribArray(pos);
      gl.vertexAttribPointer(pos, 2, gl.FLOAT, false, 0, 0);
    } else {
      console.warn('SeedShaderCanvas: Shader program invalid, skipping render.');
      return; // Skip rendering loop to prevent JS errors
    }

    const uTime = gl.getUniformLocation(prog, 'u_time');
    const uRes = gl.getUniformLocation(prog, 'u_resolution');
    const uReducedMotion = gl.getUniformLocation(prog, 'u_reduced_motion');
    const uWelcomeMode = gl.getUniformLocation(prog, 'u_welcome_mode');
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    const startTime = performance.now();

    function render(time: number) {
      if (!gl) return;
      if (!resizeObserver) syncSize();

      gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);
      const elapsed = (time - startTime) * 0.001;
      if (uTime) gl.uniform1f(uTime, elapsed);
      if (uRes) gl.uniform2f(uRes, gl.canvas.width, gl.canvas.height);
      if (uReducedMotion) gl.uniform1f(uReducedMotion, mediaQuery.matches ? 1.0 : 0.0);
      if (uWelcomeMode) gl.uniform1f(uWelcomeMode, isWelcomeMode ? 1.0 : 0.0);

      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      animFrameId = requestAnimationFrame(render);
    }

    animFrameId = requestAnimationFrame(render);

    return () => {
      cancelAnimationFrame(animFrameId);
      if (resizeObserver) resizeObserver.disconnect();
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className={className}
      style={{
        display: 'block',
        width: '100%',
        height: '100%',
        position: 'fixed',
        inset: 0,
        zIndex: 0,
        pointerEvents: 'none',
        ...style,
      }}
    />
  );
}

export default SeedShaderCanvas;
