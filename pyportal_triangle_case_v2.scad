/*
Copyright Lindsay Watt 2022. Feel free to reuse for non-commercial purposes.
*/

$fa = 1;
$fs = 1;

radius = 100; /* 1cm thick wall */
width = 665; /* 64.5mm for PyPortal plus 1mm wall on either side */
edge_length = 1254; /* Measured height of PyPortal + USB cord */
offset = 2 * radius;

module pyportalCutout() {
    // Set depth of print
    max_depth = 102;
    mounting_hole_offset = 39;
    mounting_hole_depth = max_depth - mounting_hole_offset;
    active_screen_offset = 10; /* Original depth of 5 didn't print well */

    // Screen - full
    translate([50,0,active_screen_offset])
      cube([547,776,max_depth-active_screen_offset],false);
   
    // Screen - active area
    translate([75,101,0])
        cube([497,645,active_screen_offset+1], false);
    
    // Mounting holes
    // add extra unit to combine shapes
    translate([0,0,mounting_hole_offset])
      cube([51,53,mounting_hole_depth], false);
    translate([595,0,mounting_hole_offset])
      cube([50,53,mounting_hole_depth], false);
    translate([0,831,mounting_hole_offset])
      cube([51,53,mounting_hole_depth], false);
    translate([595,831,mounting_hole_offset])
      cube([50,53,mounting_hole_depth], false);

    // Circuitboard
    translate([50,775,mounting_hole_offset])
      cube([547,459,mounting_hole_depth], false);    
}

module edge(r,w,e) {
    difference() {
        cylinder(r=2*r,h=w);
        translate([0,0,-w/2]) /* eliminate undefined edges */
            cylinder(r=r, h=2*w)
        ;
    };
    translate([0,-2*r,0])
        cube([e,r,w],center=false);
    
};

module outerShell(r,w,e) {
    edge(r, w, e);

    translate([e,0,0])
        rotate([0,0,120])
            edge(r, w, e);

    translate([e/2,e*sin(60),0])
        rotate([0,0,240])
            edge(r, w, e);
    
};


module innerGap(r,w,e,o) {
    translate([0,0,-o/2])
        linear_extrude(height = w+o)
            polygon( points=[[0,0],[e,0],[e/2,e*sin(60)], [0,0]] );

    translate([0,-r,-o/2])
            cube([e,r+1,w+o],center=false);
            
    rotate([0,0,60])
        translate([0,-1,-o/2]) /* -1 to eliminate exact edges */
            cube([e,r+1,w+o],center=false);

    translate([e,0,0])
        rotate([0,0,120])
            translate([0,-r,-o/2])
                cube([e,r+1,w+o],center=false);

};


module shell(r,w,e, o) {
    difference(){
            outerShell(r, w, e);
            innerGap(r, w, e, o);
    };    
};

module withPortal(r,w,e,o) {
    difference(){
        shell(r, w, e, o);
        rotate([0,-90,270])
            /* 1mm wall so need to offset */
            translate([10,0,-201])
                pyportalCutout();
    };
};


module plug() {
    cylinder(r=31,h=200);
    translate([0,-31,0])
        cube([53,62,200]);
    translate([53,0,0])
        cylinder(r=31,h=200);    
};

difference(){
    withPortal(radius, width, edge_length, offset);
    rotate([0,0,90])
        rotate([90,0,0])
        rotate([0,-60,0])
        translate([0,width/2,0])
        translate([1000,0,-850])
    plug();    
};






/*edge(radius, width, edge_length);*/
/*outerShell(radius, width, edge_length);
innerGap(radius, width, edge_length, offset);*/