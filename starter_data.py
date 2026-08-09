import pandas as pd


def verified_starter_data():
    products = pd.DataFrame([
        ["Men's DADE Short Sleeve Polo","TM16398","Apparel","Elevate","Black (995)"],
        ["Men's DADE Short Sleeve Polo","TM16398","Apparel","Elevate","Navy (575)"],
        ["Men's DADE Short Sleeve Polo","TM16398","Apparel","Elevate","Steel Grey (945)"],
        ["Men's DADE Short Sleeve Polo","TM16398","Apparel","Elevate","White (125)"],
        ["Men's BODIE Short Sleeve Tee","TM17879","Apparel","Elevate","Black (995)"],
        ["Men's BODIE Short Sleeve Tee","TM17879","Apparel","Elevate","White (125)"],
        ["Men's BODIE Short Sleeve Tee","TM17879","Apparel","Elevate","Medium Heather Grey (939)"],
        ["Stanley Quencher H2.O FlowState™ Tumbler 30oz","1603-02","Drinkware","Stanley","ASH"],
        ["Stanley Quencher H2.O FlowState™ Tumbler 30oz","1603-02","Drinkware","Stanley","Black (BK)"],
        ["Stanley Quencher H2.O FlowState™ Tumbler 30oz","1603-02","Drinkware","Stanley","Cream (CR)"],
        ["Stanley Quencher H2.O FlowState™ Tumbler 30oz","1603-02","Drinkware","Stanley","Frost (FRST)"],
        ["Stanley Quencher H2.O FlowState™ Tumbler 30oz","1603-02","Drinkware","Stanley","Rose Quartz (RSQTZ)"],
        ["Stanley Quencher H2.O FlowState™ Tumbler 30oz","1603-02","Drinkware","Stanley","Sky Blue"],
        ["Stanley Quencher H2.O FlowState™ Tumbler 30oz","1603-02","Drinkware","Stanley","Twilight"],
        ["FSC® Mix 5\" x 7\" Pedova™ Bound Journal","2700-02","Journals","","Black (BK)"],
        ["FSC® Mix 5\" x 7\" Pedova™ Bound Journal","2700-02","Journals","","Navy (NY)"],
        ["Pinnacle Recycled Travel Tumbler with Straw 40oz","1603-15","Drinkware","","Black (BK)"],
        ["Pinnacle Recycled Travel Tumbler with Straw 40oz","1603-15","Drinkware","","Gray (GY)"],
        ["Pinnacle Recycled Travel Tumbler with Straw 40oz","1603-15","Drinkware","","Navy (NY)"],
        ["Pinnacle Recycled Travel Tumbler with Straw 40oz","1603-15","Drinkware","","Red (RD)"],
        ["Pinnacle Recycled Travel Tumbler with Straw 40oz","1603-15","Drinkware","","White (WH)"],
        ["Hercules Non-Woven Grocery Tote","SM-7427","Bags","Bullet","Black (BK)"],
        ["Hercules Non-Woven Grocery Tote","SM-7427","Bags","Bullet","Navy Blue (NBL)"],
        ["Hercules Non-Woven Grocery Tote","SM-7427","Bags","Bullet","RED (RE)"],
        ["Hercules Non-Woven Grocery Tote","SM-7427","Bags","Bullet","White (WH)"],
        ["nutribullet® Portable Blender","1032-53","Technology","Nutribullet","White (WH)"],
        ["Hydro Flask® All Around™ Tumbler 20oz","1601-95","Drinkware","Hydro Flask","Black (BK)"],
        ["Hydro Flask® All Around™ Tumbler 20oz","1601-95","Drinkware","Hydro Flask","Harbor Blue"],
        ["Hydro Flask® All Around™ Tumbler 20oz","1601-95","Drinkware","Hydro Flask","White (WH)"],
    ], columns=["Product Name","Item Number","Product Category","Brand","Default Item Color"])
    products["Product Description"] = ""

    decorations = pd.DataFrame([
        ["TM16398","Apparel Digital Transfer","CHEST, Horizontal, - Centered on Left Chest",4,4],
        ["TM16398","Apparel Embroidery","CHEST, Horizontal, - Centered on Left Chest",4,4],
        ["TM16398","Apparel Digital Transfer","SLEEVE, Horizontal, - Centered on Right Sleeve Bicep",4,2],
        ["TM16398","Apparel Embroidery","SLEEVE, Horizontal, - Centered on Right Sleeve Bicep",4,2],
        ["TM17879","Apparel Digital Transfer","CHEST, Horizontal, - Centered on Left Chest",4,4],
        ["TM17879","Apparel Embroidery","CHEST, Horizontal, - Centered on Left Chest",4,4],
        ["TM17879","Apparel Digital Transfer","SLEEVE, Horizontal, - Centered on Right Sleeve Bicep",4,2],
        ["TM17879","Apparel Embroidery","SLEEVE, Horizontal, - Centered on Right Sleeve Bicep",4,2],
        ["1603-02","Laser","Handle Left - Opposite Stanley logo, (Front) Center of art 2.89\"",1.5,1.5],
        ["1603-02","Color Print SilkScreen - Drinkware","Handle Left - Opposite Stanley logo, (Front) Center of art 2.89\"",2.51,3.5],
        ["1603-02","Laser - Laser Plus","Handle Left - Opposite Stanley logo, (Front) Center of art 2.89\"",2.75,4.13],
        ["2700-02","Deboss","Spine Left - Centered on Front",3.5,5.5],
        ["2700-02","Deboss","Spine Left - Centered on front 1\" up from bottom",3.5,1],
        ["1603-15","Laser","Handle Left - Center of art 3\" down from lip",1.5,1.5],
        ["1603-15","Laser - Laser Plus","Handle Left - Center of art 3\" down from lip",3,4.38],
        ["1603-15","Color Print SilkScreen - Drinkware","Handle Left - Center of art 3\" down from lip",3.16,4],
        ["1603-15","Laser","Handle RIGHT - Center of art 3\" down from lip",1.5,1.5],
        ["SM-7427","Digital Print Transfer - PhotoGrafixx","Centered On Front",5,10],
        ["SM-7427","Color Print SilkScreen","Centered On Front",5,10],
        ["1032-53","Color Print SilkScreen - Drinkware","Centered on blender opposite measurements, center of art 3.25\" d",4.2,4],
        ["1601-95","Laser","Centered on tumbler opposite Hydro Flask, - Center of art 3.05\"",1.75,4],
        ["1601-95","Digital Color Print","Centered on tumbler opposite Hydro Flask, - Center of art 3.05\"",3.83,3.5],
        ["1601-95","Color Print SilkScreen - Drinkware","Centered on tumbler opposite Hydro Flask, - Center of art 3.05\"",3.83,3.5],
    ], columns=["Item Number","Decoration Method","Decoration Location","Max Length","Max Height"])

    # Verified USD LIST DECORATED schedule rows from the supplied pricing master.
    price_rows = []
    def add(item, tiers):
        for moq, unit, level in tiers:
            price_rows.append([item,moq,unit,level,"USD","USD-List-Decorated_1","USD-List-Decorated"])
    add("TM16398",[(12,27.32,"A"),(175,26.40,"A"),(350,23.18,"B"),(500,20.52,"C"),(650,19.17,"C")])
    add("1603-02",[(24,56.70,"E"),(100,54.46,"E"),(150,52.20,"E"),(250,49.96,"E"),(400,45.00,"E")])
    add("2700-02",[(50,16.62,"C"),(100,15.95,"C"),(200,15.30,"C"),(350,14.63,"C"),(500,13.18,"C")])
    add("1603-15",[(24,19.52,"C"),(100,18.73,"C"),(150,17.97,"C"),(250,17.18,"C"),(400,15.48,"C")])
    add("SM-7427",[(150,2.72,"C"),(475,2.54,"C"),(750,2.35,"C"),(1125,2.17,"C"),(1500,1.99,"C")])
    add("1601-95",[(24,41.56,"E"),(100,39.91,"E"),(150,38.26,"E"),(250,36.61,"E"),(400,32.99,"E")])
    pricing = pd.DataFrame(price_rows, columns=["Item Number","MOQ","Unit Price","Price Level ","CurrencyID","Decorated or Blank","Price Description"])
    return products, decorations, pricing
