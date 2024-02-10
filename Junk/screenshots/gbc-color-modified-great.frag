/*
   GBC Color Correction Shader
   A shader that replicates the LCD dynamics from a Game Boy Color
   Color values are derived from Gambatte's color correction implementation, with some tweaks.
   Further tweaks by Pokefan531.
   
   Based on Color Mangler
   Author: hunterk
   License: Public domain
*/

// Compatibility #ifdefs needed for parameters
#ifdef GL_ES
#define COMPAT_PRECISION mediump
#else
#define COMPAT_PRECISION
#endif

#pragma parameter brighten_screen "Brighten Screen" 0.5 -0.25 1.0 0.05
#ifdef PARAMETER_UNIFORM
// All parameter floats need to have COMPAT_PRECISION in front of them
uniform COMPAT_PRECISION float brighten_screen;
#else
#define brighten_screen -0.333
#endif

#define target_gamma  2.0
#define display_gamma 2.0
#define sat 1.12
#define lum 1.1
#define blr 0.0
#define blg 0.0
#define blb 0.0
// #define r 0.87
// #define g 0.66
// #define b 0.79
// #define rg 0.115
// #define rb 0.14
// #define gr 0.18
// #define gb 0.07
// #define br -0.05
// #define bg 0.225
#define r  0.95
#define g  0.75
#define b  0.85
#define rg 0.115
#define rb 0.14
#define gr 0.18
#define gb 0.07
#define br -0.05
#define bg 0.225

#if __VERSION__ >= 130
#define COMPAT_VARYING in
#define COMPAT_TEXTURE texture
out vec4 FragColor;
#else
#define COMPAT_VARYING varying
#define FragColor gl_FragColor
#define COMPAT_TEXTURE texture2D
#endif

#ifdef GL_ES
#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif
#define COMPAT_PRECISION mediump
#else
#define COMPAT_PRECISION
#endif

uniform COMPAT_PRECISION int FrameDirection;
uniform COMPAT_PRECISION int FrameCount;
uniform COMPAT_PRECISION vec2 OutputSize;
uniform COMPAT_PRECISION vec2 TextureSize;
uniform COMPAT_PRECISION vec2 InputSize;
uniform sampler2D u_tex0;
// COMPAT_VARYING vec4 TEX0;

// compatibility #defines
varying vec2 v_texcoord;

#define SourceSize vec4(TextureSize, 1.0 / TextureSize) //either TextureSize or InputSize
#define outsize vec4(OutputSize, 1.0 / OutputSize)

void main()
{
   vec4 screen = pow(texture2D(u_tex0, v_texcoord), vec4(target_gamma + brighten_screen)).rgba;

   //                red   green  blue  alpha ; alpha does nothing for our purposes
   mat4 color = mat4(r,    rg,    rb,   1.0,    //red
                     gr,   g,     gb,   1.0,    //green
                     br,   bg,    b,    1.0,    //blue
                     blr,  blg,   blb,  1.0);   //black

   mat4 adjust = mat4((1.0 - sat) * 0.2126 + sat, (1.0 - sat) * 0.2126, (1.0 - sat) * 0.2126, 1.0,
                      (1.0 - sat) * 0.7152, (1.0 - sat) * 0.7152 + sat, (1.0 - sat) * 0.7152, 1.0,
                      (1.0 - sat) * 0.0722, (1.0 - sat) * 0.0722, (1.0 - sat) * 0.0722 + sat, 1.0,
                      0.0, 0.0, 0.0, 1.0);
   
   color *= adjust;

   screen = clamp(screen * lum, 0.0, 1.0);

   screen = color * screen;
   gl_FragColor = pow(screen, vec4(1.0 / display_gamma));
}
