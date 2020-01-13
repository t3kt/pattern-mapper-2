#include "shape_shader_shared"

uniform sampler2D sTexture0;
uniform sampler2D sTexture1;
uniform sampler2D sTexture2;
uniform sampler2D sTexture3;

in Vertex {
	VertexAttrs attrs;
} iVert;

sampler2D getTexture() {
	switch (iVert.attrs.appearance.texSource) {
		case 0: return sTexture0;
		case 1: return sTexture1;
		case 2: return sTexture2;
		case 3: return sTexture3;
		default: return sTexture0;
	}
}

out vec4 fragColor;
void main() {
	TDCheckDiscard();

	vec4 color = iVert.attrs.color;

	if (iVert.attrs.appearance.opacity <= 0) {
		color = vec4(0);
	} else {
		color = iVert.attrs.appearance.color;
//		if (iVert.attrs.appearance.color.a > 0) {
//			color.rgb = mix(color.rgb, iVert.attrs.appearance.color.rgb, iVert.attrs.appearance.color.a);
//		}
		if (iVert.attrs.appearance.texOpacity > 0) {
//			vec2 coord = iVert.attrs.texCoord.xy;
//			coord = vec2(0.5);
//			vec4 texColor = texture(getTexture(), coord);
//			color = mix(color, texColor, iVert.attrs.appearance.texOpacity);
//			color = texColor;
		}
		color.a *= iVert.attrs.appearance.opacity;
	}
	TDAlphaTest(color.a);
	fragColor = TDOutputSwizzle(color);
}

