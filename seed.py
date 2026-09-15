import json
CATEGORIES = [
 ('architects','Famous architects','The minds behind the masterpieces','architects','01'),
 ('world','World architecture','A journey through iconic places','world','02'),
 ('uae','UAE architecture','Our heritage. Our future.','uae','03'),
 ('history','Architecture history','From ancient to avant-garde','history','04'),
 ('structures','Structures & materials','The science behind the skyline','structures','05'),
 ('sustainability','Sustainable design','Designing a better tomorrow','sustainability','06'),
 ('drawing','Architectural drawing','Read between the lines','world','07'),
 ('buildings','Famous buildings','Recognize the remarkable','architects','08'),
 ('urban','Urban design','How cities come together','uae','09'),
 ('theory','Architecture theory','Ideas that shaped our spaces','history','10'),
 ('digital','Digital design','From algorithm to architecture','structures','11'),
 ('bim','CAD & BIM','Beyond the drawing board','world','12'),
 ('interior','Interior architecture','The world within','sustainability','13'),
 ('mystery','Architecture mystery','Follow the architectural clues','architects','14'),
 ('climate','Gulf & climate','Built for this place','uae','15'),
 ('speed','Speed round','Think fast. Build points.','structures','16')]
# Each row: prompt, accepted answer, teaching note. Optional options/image/type.
BANK={
'architects':[
('Who designed Fallingwater in Pennsylvania?','Frank Lloyd Wright','Wright integrated the house with the waterfall and its rocky landscape.',['Frank Lloyd Wright','Frank Gehry','Louis Kahn','Alvar Aalto']),
('Which Iraqi-born architect became the first woman to receive the Pritzker Architecture Prize?','Zaha Hadid','Hadid received the prize in 2004.',['Zaha Hadid','Lina Bo Bardi','Kazuyo Sejima','Marina Tabassum']),
('Match these architects to their works: Gaudí, I. M. Pei, Mies van der Rohe. Works: Louvre Pyramid, Barcelona Pavilion, Sagrada Família.','Gaudí — Sagrada Família; I. M. Pei — Louvre Pyramid; Mies van der Rohe — Barcelona Pavilion','The three works span expressive Catalan architecture, a glass museum entrance, and modernist spatial experimentation.'),
('Who designed the National Assembly Building in Dhaka, Bangladesh?','Louis Kahn','Kahn used monumental geometry, light, and water in this civic complex.',['Louis Kahn','Oscar Niemeyer','Le Corbusier','Tadao Ando']),
('Which Egyptian architect wrote Architecture for the Poor and championed earthen construction at New Gourna?','Hassan Fathy','Fathy advocated climate-responsive design and local building knowledge.',['Hassan Fathy','Rasem Badran','Balkrishna Doshi','Geoffrey Bawa'])],
'world':[
('In which country is the Taj Mahal?','India','The Mughal mausoleum stands in Agra.',['India','Iran','Türkiye','Pakistan']),
('The Sydney Opera House was designed by which Danish architect?','Jørn Utzon','Utzon won the international competition in 1957.',['Jørn Utzon','Eero Saarinen','Renzo Piano','Santiago Calatrava']),
('Which came first: the Great Pyramid of Giza or the Parthenon?','Great Pyramid of Giza','The Great Pyramid dates to the third millennium BCE; the Parthenon to the fifth century BCE.',['Great Pyramid of Giza','Parthenon']),
('In which city is Moshe Safdie’s Habitat 67?','Montreal','The modular housing complex was built for Expo 67.',['Montreal','Toronto','Vancouver','Quebec City']),
('The Great Mosque of Djenné is primarily associated with which architectural tradition?','Sudano-Sahelian','Its earthen construction and projecting timber toron are characteristic of the regional tradition.',['Sudano-Sahelian','Mughal','Ottoman','Timurid'])],
'uae':[
('What is the name of the world’s tallest completed building, located in Dubai?','Burj Khalifa','The tower opened in 2010 and is 828 metres tall.',['Burj Khalifa','Burj Al Arab','Cayan Tower','Dubai Frame']),
('Who designed the Louvre Abu Dhabi?','Jean Nouvel','The dome produces the museum’s celebrated rain-of-light effect.',['Jean Nouvel','Norman Foster','Frank Gehry','Zaha Hadid']),
('What is the traditional Gulf wind tower commonly called in the UAE?','Barjeel','Wind towers channel air to improve ventilation and cooling.',['Barjeel','Mashrabiya','Mihrab','Iwan']),
('Which practice designed Dubai’s Museum of the Future?','Killa Design','Killa Design developed its distinctive torus-shaped form.',['Killa Design','Foster + Partners','OMA','SOM']),
('Burj Khalifa’s primary structural concept is known as what?','Buttressed core','Three wings support a central hexagonal core, providing lateral stability.',['Buttressed core','Diagrid tube','Suspended mast','Unreinforced shell'])],
'history':[
('Pointed arches, rib vaults, and flying buttresses are associated with which style?','Gothic','These elements enabled tall, light-filled medieval churches.',['Gothic','Doric','Bauhaus','Brutalism']),
('True or false: the Bauhaus was founded in Germany in 1919.','True','Walter Gropius founded the school in Weimar.',['True','False']),
('Put these movements in chronological order: Baroque, Romanesque, Renaissance.','Romanesque → Renaissance → Baroque','Romanesque preceded the Renaissance, followed by Baroque architecture.'),
('Which system of triangular curved surfaces transitions a square bay to a circular dome, as at Hagia Sophia?','Pendentives','Pendentives transfer dome loads toward the supporting piers.',['Pendentives','Tracery','Voussoirs','Pilasters']),
('Which Renaissance architect developed the double-shell dome of Florence Cathedral?','Filippo Brunelleschi','The dome was constructed without conventional full timber centering.',['Filippo Brunelleschi','Leon Battista Alberti','Andrea Palladio','Donato Bramante'])],
'structures':[
('Which structural element primarily carries vertical loads in compression?','Column','Columns transfer loads from floors and roofs toward foundations.',['Column','Handrail','Flashing','Gutter']),
('Identify the structural system in this schematic.','Triangulated truss','Triangulation provides geometric stability; idealized truss members carry axial forces.',['Triangulated truss','Flat slab','Shell','Masonry arch'],'truss.svg'),
('Why is steel reinforcement commonly placed near the bottom of a simply supported concrete beam under downward load?','To resist tensile stresses','Positive bending creates tension in the lower region; concrete is weak in tension.'),
('Which material property relates elastic stress to strain in the linear range?','Young’s modulus','It measures axial elastic stiffness.',['Young’s modulus','Poisson’s ratio','Thermal conductivity','Density']),
('For an ideal Euler column, how does the critical buckling load change if effective length doubles, with all else fixed?','It falls to one quarter','Euler critical load is inversely proportional to the square of effective length.',['It falls to one quarter','It doubles','It halves','It is unchanged'])],
'sustainability':[
('Which energy source do photovoltaic panels convert into electricity?','Sunlight','Photovoltaic cells directly convert light into electrical energy.',['Sunlight','Wind','Geothermal heat','Rainfall']),
('True or false: external shading can reduce solar heat gain before sunlight reaches glazing.','True','External shading intercepts incident solar radiation.',['True','False']),
('What is embodied carbon?','Greenhouse gas emissions associated with materials and construction over their life cycle','It includes processes such as extraction, manufacturing, transport, construction, and end of life.'),
('What does a lower U-value generally indicate about a building element?','Less heat transmission','U-value measures thermal transmittance, usually in W/m²K.',['Less heat transmission','More daylight','More thermal expansion','Less airtightness']),
('Why can night-purge ventilation with thermal mass be ineffective in a hot, humid climate with warm nights?','The outdoor air may not be cool enough to remove stored heat and can add moisture','Night flushing requires an adequate temperature difference and suitable humidity conditions.')],
'drawing':[
('What type of architectural drawing is shown?','Floor plan','A plan is a horizontal sectional view, conventionally looking downward.',['Floor plan','Elevation','Perspective','Site section'],'plan.svg'),
('At a scale of 1:100, what real length does 1 cm on paper represent?','1 metre','Multiply the drawing measurement by 100.',['1 metre','10 metres','10 centimetres','100 metres']),
('Identify the drawing that cuts vertically through a building.','Section','A section reveals internal levels, spaces, and construction.',['Section','Roof plan','Axonometric','Reflected ceiling plan'],'section.svg'),
('How does an orthographic elevation differ from a perspective view?','Parallel projection without perspective convergence','An elevation shows a face without foreshortening caused by distance from the viewer.'),
('A slope rises 750 mm over a horizontal run of 9 m. Express its gradient as 1:n.','1:12','9000 divided by 750 is 12.',['1:12','1:9','1:15','1:20'])],
'buildings':[
('Which Paris landmark was built for the 1889 Exposition Universelle?','Eiffel Tower','The iron lattice tower was constructed by Gustave Eiffel’s company.',['Eiffel Tower','Louvre Pyramid','Arc de Triomphe','Centre Pompidou']),
('Who designed the Guggenheim Museum Bilbao?','Frank Gehry','The museum is known for its curving titanium-clad forms.',['Frank Gehry','Frank Lloyd Wright','Philip Johnson','Norman Foster']),
('Match the buildings to cities: Petronas Towers, Salk Institute, Centre Pompidou.','Petronas Towers — Kuala Lumpur; Salk Institute — La Jolla; Centre Pompidou — Paris','These are landmarks by César Pelli, Louis Kahn, and Renzo Piano with Richard Rogers respectively.'),
('Tadao Ando’s Church of the Light is in which country?','Japan','Its cruciform opening brings light into a restrained concrete interior.',['Japan','South Korea','China','Vietnam']),
('Which architect designed the Paimio Sanatorium, including many of its interior details?','Alvar Aalto','The Finnish sanatorium exemplifies Aalto’s human-centered modernism.',['Alvar Aalto','Eero Saarinen','Arne Jacobsen','Gunnar Asplund'])],
'urban':[
('What do we call a public open space usually enclosed by buildings?','Square','A square or plaza is a gathering place within the urban fabric.',['Square','Setback','Duct','Plenum']),
('What does mixed-use development combine?','Different uses such as housing, shops, and workplaces','Mixing uses can shorten trips and support activity throughout the day.'),
('Who wrote The Death and Life of Great American Cities?','Jane Jacobs','Jacobs emphasized street life, diversity, and observation.',['Jane Jacobs','Kevin Lynch','Ebenezer Howard','Lewis Mumford']),
('Name the five elements of urban imageability identified by Kevin Lynch.','Paths, edges, districts, nodes, landmarks','Lynch presented these in The Image of the City.'),
('Which planning concept associated with Ebenezer Howard combines town and country in settlements surrounded by green belts?','Garden city','Howard proposed linked, self-contained settlements with access to countryside.',['Garden city','Radiant city','Broadacre City','Linear city'])],
'theory':[
('The phrase “form follows function” is most associated with whom?','Louis Sullivan','Sullivan used the phrase in his writing on tall office buildings.',['Louis Sullivan','Antoni Gaudí','Robert Venturi','Peter Zumthor']),
('Which architect is closely associated with “less is more”?','Ludwig Mies van der Rohe','The phrase is associated with his restrained modernist approach.',['Ludwig Mies van der Rohe','Frank Gehry','Oscar Niemeyer','Moshe Safdie']),
('Name the three Vitruvian qualities, often translated as firmness, commodity, and delight.','Firmitas, utilitas, venustas','They concern durability, usefulness, and beauty.'),
('Which book by Robert Venturi challenged orthodox modernist simplicity in 1966?','Complexity and Contradiction in Architecture','Venturi argued for richness, ambiguity, and layered architectural meaning.',['Complexity and Contradiction in Architecture','Delirious New York','Towards a New Architecture','The Eyes of the Skin']),
('Which critic is closely associated with the essay Towards a Critical Regionalism: Six Points for an Architecture of Resistance?','Kenneth Frampton','Frampton argued for architecture attentive to place, tectonics, and local conditions.',['Kenneth Frampton','Reyner Banham','Charles Jencks','Aldo Rossi'])],
'digital':[
('What does 3D stand for?','Three-dimensional','Digital 3D models represent three spatial dimensions.',['Three-dimensional','Three details','Third drawing','Three designs']),
('Which visual programming environment is integrated with Rhino?','Grasshopper','Grasshopper uses connected components to define computational workflows.',['Grasshopper','InDesign','Excel','Lumion']),
('What is parametric design?','Design defined by parameters and relationships','Changing parameters can propagate controlled changes through a model.'),
('What distinguishes a mesh from a NURBS surface?','A mesh uses discrete polygon faces; NURBS uses mathematically defined curves and surfaces','Both represent geometry but have different editing and precision characteristics.'),
('In multi-objective optimization, what is a Pareto-optimal solution?','A solution where improving one objective requires worsening at least one other objective','The Pareto front contains non-dominated trade-offs.')],
'bim':[
('What does BIM stand for?','Building Information Modeling','BIM involves structured information about built assets.',['Building Information Modeling','Basic Interior Mapping','Building Image Making','Blueprint Integration Method']),
('What is the main purpose of clash detection?','To identify conflicts between coordinated building systems','For example, a duct may intersect a structural beam.'),
('Which open standard is commonly used to exchange BIM model information between software platforms?','IFC','Industry Foundation Classes is an open data schema.',['IFC','JPEG','MP3','CSS']),
('In BIM terminology, what does 4D commonly add to a 3D model?','Time or construction scheduling','Linking model elements to time supports construction sequencing.',['Time or construction scheduling','Acoustics','Color','Latitude']),
('What is a common data environment in an information-management workflow?','An agreed source for collecting, managing, and sharing project information','A CDE combines workflow and technical solutions, not merely a shared folder.')],
'interior':[
('Which discipline studies the fit between people and their physical environment or equipment?','Ergonomics','Ergonomics informs dimensions, reach, posture, and usability.',['Ergonomics','Geology','Hydrology','Cartography']),
('Which lighting layer is intended for a specific activity such as reading?','Task lighting','Task lighting supplements general illumination.',['Task lighting','Accent lighting','Emergency lighting','Facade lighting']),
('What is reverberation time?','The time for sound level to decay by 60 dB after a source stops','It is a key indicator of room acoustics.'),
('What does a material’s light reflectance value describe?','The proportion of visible light reflected by its surface','LRV helps assess contrast and distribution of light.'),
('Why can adding absorptive wall panels improve speech intelligibility in a reverberant room?','They reduce reflected sound energy and reverberation','They do not necessarily provide sound isolation between rooms.')],
'mystery':[
('Exposed concrete, monumental geometric forms, and minimal ornament: which movement is suggested?','Brutalism','Brutalism often emphasizes raw materials and powerful massing.',['Brutalism','Rococo','Art Nouveau','Gothic']),
('I am supported at one end and project freely at the other. What am I?','Cantilever','A cantilever transfers bending and shear into its fixed support.',['Cantilever','Simply supported beam','Dome','Column']),
('I have pilotis, a roof garden, a free plan, a free façade, and ribbon windows. Whose Five Points do I illustrate?','Le Corbusier','The Five Points were developed by Le Corbusier, with Pierre Jeanneret.'),
('My dome has an open oculus; I stand in Rome and my ancient concrete dome remains unreinforced. Name me.','Pantheon','The Pantheon’s dome uses graded aggregates and coffering.',['Pantheon','Colosseum','St Peter’s Basilica','Basilica of Maxentius']),
('A desert office has unshaded west glazing, high internal heat gains, and no glare control. Identify two design problems and propose a response.','Excess solar heat and glare; reduce or externally shade west glazing and manage internal loads','Host judges reasonable evidence-based alternatives. This is a design diagnosis, not a single-answer code question.')],
'climate':[
('Why are shaded pedestrian routes valuable in UAE cities?','They reduce exposure to direct solar radiation','Shade improves outdoor thermal comfort, though air temperature and humidity also matter.'),
('Which traditional Gulf house element creates a protected outdoor space within the building?','Courtyard','Courtyards can provide privacy, shade, and opportunities for ventilation.',['Courtyard','Curtain wall','Escalator','Atrium exhaust fan']),
('Why is low-angle west sun often difficult to control using only horizontal overhangs?','It passes beneath shallow horizontal shading','Vertical fins, screens, or reduced west glazing can be more effective.'),
('In humid coastal Gulf conditions, what indoor problem can excessive infiltration cause in air-conditioned buildings?','Moisture loads and condensation risk','Warm humid air can condense on surfaces below its dew point.'),
('Why does high thermal mass alone not guarantee low cooling demand in a continuously hot climate?','Stored heat needs a way to be discharged; insulation, shading, and operating conditions matter','Mass delays heat flow but cannot eliminate accumulated heat without a heat sink.')],
'speed':[
('Name the horizontal structural element that spans between supports.','Beam','A beam commonly resists bending.'),
('What is the topmost central stone of an arch called?','Keystone','The keystone sits at the crown of a masonry arch.'),
('What is a building’s outer face commonly called?','Façade','Facade is also accepted.'),
('What is the unit of thermal transmittance, U-value?','W/m²K','Watts per square metre per kelvin.'),
('What is the ratio of lateral strain to axial strain, with a negative sign, called?','Poisson’s ratio','It describes transverse deformation under axial loading.')]
}
def questions():
 out=[]
 for cat,rows in BANK.items():
  for i,row in enumerate(rows):
   q,a,e,*rest=row;opts=rest[0] if rest else []
   image='/assets/'+rest[1] if len(rest)>1 else ''
   typ='image' if image else 'truefalse' if opts==['True','False'] else 'choice' if opts else 'match' if q.startswith('Match') else 'timeline' if 'chronological' in q else 'open'
   out.append(dict(id=f'{cat}-{i+1}',category=cat,difficulty=i+1,points=(i+1)*100,type=typ,question=q,options=opts,correctAnswer=a,explanation=e,image=image,source='Editorial seed • verify against course references before your event',timeLimit=30,hint=e if cat=='mystery' else 'Discuss the defining terms in the question.',tolerance=0))
 return out
FINAL=dict(id='final-1',category='theory',difficulty=5,points=0,type='open',question='Name all five points of a new architecture proposed by Le Corbusier, and identify the villa in Poissy that famously demonstrates them.',options=[],correctAnswer='Pilotis; roof garden; free plan; free façade; horizontal ribbon windows. Villa Savoye.',explanation='Villa Savoye, designed with Pierre Jeanneret, is a canonical demonstration of the Five Points. Host judges completeness.',image='',source='Le Corbusier — Five Points of a New Architecture',timeLimit=60,hint='Think of structure, envelope, ground, and roof.')

_original_questions = questions
def questions():
 out = _original_questions()
 out.extend([dict(id='uae-visual',category='uae',difficulty=2,points=200,type='image',question='Identify this Dubai landmark from its conceptual silhouette.',options=['Burj Al Arab','Cayan Tower','Dubai Frame','Etihad Museum'],correctAnswer='Burj Al Arab',explanation='The sail-shaped hotel was designed by Tom Wright at Atkins. Illustration is schematic, not a measured elevation.',image='/assets/burj-sketch.svg',source='Original schematic illustration; building attribution: Atkins',timeLimit=30,hint='It stands on an artificial island.'),dict(id='materials-visual',category='structures',difficulty=1,points=100,type='image',question='Which masonry bond is shown in this schematic?',options=['Running bond','Stack bond','English bond','Flemish bond'],correctAnswer='Running bond',explanation='Stretcher courses are offset, typically by half a brick. This diagram omits construction details.',image='/assets/brick.svg',source='Original schematic illustration',timeLimit=30,hint='Adjacent courses are offset.'),dict(id='drawing-visual',category='drawing',difficulty=2,points=200,type='image',question='Identify this orthographic drawing type.',options=['Elevation','Floor plan','Section','Perspective'],correctAnswer='Elevation',explanation='An elevation shows a vertical exterior face without a cutting plane.',image='/assets/elevation.svg',source='Original schematic illustration',timeLimit=30,hint='You are looking at the outside face.')])
 return out

_base_questions = questions
def questions():
 out = _base_questions()
 additions = [
 ('history',2,'Identify the ancient Roman amphitheatre in this photograph.','Colosseum','The Flavian Amphitheatre, commonly called the Colosseum, stands in Rome.',['Colosseum','Pantheon','Theatre of Epidaurus','Circus Maximus'],'/assets/history.jpg'),
 ('uae',1,'Which city’s skyline is shown in this photograph?','Dubai','Burj Khalifa is the defining vertical landmark in this Dubai skyline.',['Dubai','Abu Dhabi','Doha','Manama'],'/assets/uae.jpg'),
 ('structures',2,'Which façade system is most clearly suggested by the glass-clad office towers in this photograph?','Glazed curtain wall','Curtain walls are non-load-bearing exterior envelopes supported by the main structure.',['Glazed curtain wall','Load-bearing adobe','Exposed rammed earth','Dry-stone masonry'],'/assets/structures.jpg'),
 ('uae',3,'Which architect, working at Atkins, designed the sail-shaped Burj Al Arab?','Tom Wright','The hotel’s silhouette evokes the sail of a dhow.',['Tom Wright','Adrian Smith','Shaun Killa','Jean Nouvel'],''),
 ('uae',4,'Who won the 2009 ThyssenKrupp Elevator Architecture Award competition with the concept that became Dubai Frame?','Fernando Donis','The competition concept was developed by Fernando Donis. This asks about the winning concept, not later delivery contracts.',['Fernando Donis','Santiago Calatrava','Bjarke Ingels','Santiago Cirugeda'],''),
 ('uae',3,'Which practice developed the original masterplan for Masdar City?','Foster + Partners','The masterplan emphasized compact urban form and climate-responsive design.',['Foster + Partners','OMA','BIG','Killa Design'],''),
 ('uae',3,'Who designed the House of Wisdom in Sharjah?','Foster + Partners','The library and cultural centre uses a large overhanging roof and shaded outdoor spaces.',['Foster + Partners','Zaha Hadid Architects','SOM','Atelier Jean Nouvel'],''),
 ('uae',4,'Which Canadian practice designed the Etihad Museum in Dubai?','Moriyama & Teshima Architects','The pavilion’s form evokes a manuscript, referencing the UAE’s founding agreement.',['Moriyama & Teshima Architects','Safdie Architects','Diamond Schmitt','KPMB Architects'],''),
 ('uae',1,'In which emirate is the Sheikh Zayed Grand Mosque?','Abu Dhabi','The mosque is a major religious and cultural landmark in the UAE capital.',['Abu Dhabi','Sharjah','Dubai','Ajman'],''),
 ('architects',4,'Which Palestinian-Jordanian architect is associated with the redevelopment of the Qasr al-Hukm area in Riyadh?','Rasem Badran','Badran’s work engages with regional urban traditions and contemporary civic life.',['Rasem Badran','Hassan Fathy','Geoffrey Bawa','Balkrishna Doshi'],''),
 ('architects',4,'Who designed the Bait Ur Rouf Mosque in Dhaka?','Marina Tabassum','The mosque uses brick, daylight, and ventilation to create a contemplative space.',['Marina Tabassum','Yasmeen Lari','Muzharul Islam','Balkrishna Doshi'],''),
 ('architects',4,'Which Indian architect designed the Aranya low-cost housing project in Indore?','Balkrishna Doshi','Aranya allows incremental growth and varied housing within an organized urban framework.',['Balkrishna Doshi','Charles Correa','Laurie Baker','Raj Rewal'],''),
 ('architects',3,'Which architect’s practice designed the HSBC Main Building in Hong Kong?','Norman Foster','The building is a prominent example of high-tech architecture.',['Norman Foster','Richard Rogers','Renzo Piano','I. M. Pei'],''),
 ('architects',3,'Who designed many of the principal civic buildings of Brasília, including its cathedral?','Oscar Niemeyer','Niemeyer designed major buildings; Lúcio Costa developed the city’s pilot plan.',['Oscar Niemeyer','Lúcio Costa','Paulo Mendes da Rocha','Lina Bo Bardi'],''),
 ('theory',4,'Who wrote Delirious New York: A Retroactive Manifesto for Manhattan?','Rem Koolhaas','Published in 1978, the book examines Manhattan’s culture of congestion.',['Rem Koolhaas','Aldo Rossi','Bernard Tschumi','Robert Venturi'],''),
 ('buildings',3,'Who designed the original TWA Flight Center at New York’s JFK Airport?','Eero Saarinen','Its sculptural concrete forms suggest movement and flight.',['Eero Saarinen','Santiago Calatrava','Alvar Aalto','Philip Johnson'],''),
 ('buildings',2,'Which two architects are principally credited with designing the Centre Pompidou in Paris?','Renzo Piano and Richard Rogers','The project made its service systems and structural elements visually prominent.',['Renzo Piano and Richard Rogers','Norman Foster and Frank Gehry','Jean Nouvel and I. M. Pei','Rem Koolhaas and Bjarke Ingels'],'')]
 for n,(c,d,q,a,e,opts,img) in enumerate(additions):
  out.append(dict(id=f'collection-{n+1}',category=c,difficulty=d,points=d*100,type='image' if img else 'choice',question=q,correctAnswer=a,options=opts,explanation=e,image=img,source='Editorial collection • review with official building or architect references. Photo credits in SOURCES.md.' if img else 'Editorial collection • review with official building or architect references.',timeLimit=30,hint='Look for the defining regional, historical, or formal characteristics.',tolerance=0))
 return out

_editorial_questions = questions
def questions():
 out = _editorial_questions()
 image_keys = {'/assets/plan.svg': '/assets/q-v00.svg', '/assets/truss.svg': '/assets/q-v01.svg', '/assets/section.svg': '/assets/q-v02.svg', '/assets/elevation.svg': '/assets/q-v03.svg', '/assets/brick.svg': '/assets/q-v04.svg', '/assets/burj-sketch.svg': '/assets/q-v05.svg', '/assets/history.jpg': '/assets/q-v06.jpg', '/assets/uae.jpg': '/assets/q-v07.jpg', '/assets/structures.jpg': '/assets/q-v08.jpg'}
 for q in out:
  q["image"] = image_keys.get(q["image"],q["image"])
 return out
