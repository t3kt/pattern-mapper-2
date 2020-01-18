#include "shape_shader_shared"

uniform sampler2D sTexture0;
uniform sampler2D sTexture1;
uniform sampler2D sTexture2;
uniform sampler2D sTexture3;

in Vertex {
	VertexAttrs attrs;
} iVert;

void applyTexture(inout vec4 color, in sampler2D tex) {
	vec2 coord = iVert.attrs.texCoord.xy;
	coord = vec2(0.5);
	vec4 texColor = texture(tex, coord);
	color = mix(color, texColor, iVert.attrs.appearance.texOpacity);
	color = texColor;
}

out vec4 fragColor;
void main() {
	TDCheckDiscard();

	vec4 color = iVert.attrs.color;

	if (iVert.attrs.appearance.opacity <= 0) {
		color = vec4(0);
	} else {
		color = iVert.attrs.appearance.color;
		if (iVert.attrs.appearance.color.a > 0) {
			color.rgb = mix(color.rgb, iVert.attrs.appearance.color.rgb, iVert.attrs.appearance.color.a);
		}
		if (iVert.attrs.appearance.texOpacity > 0) {
			int texSrc = iVert.attrs.appearance.texSource;
			if (texSrc == 0) {
				applyTexture(color, sTexture0);
			} else if (texSrc == 1) {
				applyTexture(color, sTexture1);
			} else if (texSrc == 2) {
				applyTexture(color, sTexture2);
			} else if (texSrc == 3) {
				applyTexture(color, sTexture3);
			} else {
				applyTexture(color, sTexture0);
			}
		}
		color.a *= iVert.attrs.appearance.opacity;
	}
	TDAlphaTest(color.a);
	fragColor = TDOutputSwizzle(color);
}

