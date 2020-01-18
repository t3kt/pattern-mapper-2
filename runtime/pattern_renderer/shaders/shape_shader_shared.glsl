#ifdef MACOS
#define STRUCT_FLAT(x)	x
#else
#define STRUCT_FLAT(x) flat x
#endif


struct Transform {
	vec3 translate;
	vec3 rotate;
	vec3 scale;
	vec3 pivot;
};

struct Appearance {
	vec4 color;
	float opacity;
	float texOpacity;
	STRUCT_FLAT(int texSource);
};

#define UVMODE_LOCAL  0
#define UVMODE_GLOBAL 1
#define UVMODE_PATH 2

struct UVAttrs {
	STRUCT_FLAT(int uvMode);
	vec3 offset;
	float rotate;
	float scale;
};

struct VertexAttrs {
	vec4 color;
	vec3 worldSpacePos;
	STRUCT_FLAT(int shapeIndex);
	vec3 texCoord;
	Appearance appearance;
};

// https://gist.github.com/onedayitwillmake/3288507
mat4 rotationX( in float angle ) {
	return mat4(	1.0,		0,			0,			0,
			 		0, 	cos(angle),	-sin(angle),		0,
					0, 	sin(angle),	 cos(angle),		0,
					0, 			0,			  0, 		1);
}
mat4 rotationY( in float angle ) {
	return mat4(	cos(angle),		0,		sin(angle),	0,
			 				0,		1.0,			 0,	0,
					-sin(angle),	0,		cos(angle),	0,
							0, 		0,				0,	1);
}
mat4 rotationZ( in float angle ) {
	return mat4(	cos(angle),		-sin(angle),	0,	0,
			 		sin(angle),		cos(angle),		0,	0,
							0,				0,		1,	0,
							0,				0,		0,	1);
}

mat4 rotationXYZ(in vec3 r) {
	return rotationX(r.x) * rotationY(r.y) * rotationZ(r.z);
}

mat4 translateMatrix(in vec3 t) {
	return mat4(
		1.0, 0.0, 0.0, t.x,
		0.0, 1.0, 0.0, t.y,
		0.0, 0.0, 1.0, t.z,
		0.0, 0.0, 0.0, 1.0);
}

mat4 scaleMatrix(in vec3 s) {
	return mat4(
		s.x, 0.0, 0.0, 0.0,
		0.0, s.y, 0.0, 0.0,
		0.0, 0.0, s.z, 0.0,
		0.0, 0.0, 0.0, 1.0);
}

void scaleRotateTranslate(
		inout vec4 pos,
		in vec3 scale,
		in vec3 rotate,
		in vec3 translate,
		in vec3 pivot,
		in vec3 rotateAxis) {
	pos.xyz -= pivot;
	pos *= rotationXYZ(-radians(rotateAxis));

	pos *= scaleMatrix(scale);
	pos *= rotationXYZ(rotate);
	pos.xyz += translate;

	pos *= rotationXYZ(radians(rotateAxis));
	pos.xyz += pivot;
}

void applyTransform(inout vec4 pos, in Transform transform, in vec3 rotateAxis) {
	scaleRotateTranslate(
		pos,
		transform.scale,
		transform.rotate,
		transform.translate,
		transform.pivot,
		rotateAxis
	);
}
