using System;
using System.Globalization;
using System.Threading;
using YAFC;
using YAFC.Model;
using YAFC.Parser;
using System.Text.Json;
using System.Text.Json.Serialization;
//using Newtonsoft.Json;
//using Newtonsoft.Json;
//using Newtonsoft.Json.Serialization;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography.X509Certificates;
using System.Diagnostics;
using System.Reflection;
using Newtonsoft.Json.Linq;
using System.Net.NetworkInformation;
using System.Drawing.Printing;
//using static YAFC.UI.ImGuiCache<T, TKey>;
//using Newtonsoft.Json;
//using System.Collections.Generic;
//using System.IO;
//using System.Linq;
//using System.Reflection;
//using System.Text.Json.Serialization;

namespace CommandLineToolExample
{
    // If you wish to embed yafc or make a command-line tool using YAFC, here is an example on how to do that
    // However, I can't make any promises about not changing signatures
    public static class Program
    {
        public static Dictionary<string, object> ConvertFromObjectToDictionary(object arg)
        {
            return arg.GetType().GetProperties().ToDictionary(property => property.Name, property => property.GetValue(arg));
        }

        public static void Main(string[] args)
        {
            string factorioPath = "";
            bool debug = false;
            if (args.Length == 0)
            {
                Console.WriteLine("Pass FactorioData path as command-line argument");
                debug = true;
                factorioPath = "C:/Users/tuhe/AppData/Roaming/Factorio/mods";
                factorioPath = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Factorio\\data";
            }
            else
            {
                factorioPath = args[0];
            }
            string modPath = "";
            if (args.Length <= 1)
            {
                // Enable this for debug.
                modPath = "C:\\Users\\tuhe\\AppData\\Roaming\\Factorio\\mods";
            }
            else
            {
                modPath = args[1];
            }
            
            //string modPath = args[1];


            Console.WriteLine("Debug mode: " + debug + " path " + factorioPath);
            Console.WriteLine(">> initializing...");
            YafcLib.Init();
            YafcLib.RegisterDefaultAnalysis(); // Register analysis to get cost, milestones, accessibility, etc information. Skip if you just need data. 
            
            
            var errorCollector = new ErrorCollector();
            Project project;
            try
            {
                // Load YAFC project.
                // Empty project path loads default project (with one empty page).
                // Project is irrelevant if you just need data, but you need it to perform sheet calculations
                // Set to not render any icons
                Console.WriteLine(">> parsing datasource...");
                project = FactorioDataSource.Parse(factorioPath, modPath, "", false, new ConsoleProgressReport(), errorCollector, "en", false);
            }
            catch (Exception ex)
            {
                // Critical errors that make project un-loadable will be thrown as exceptions
                Console.Error.WriteException(ex);
                return;
            }
            if (errorCollector.severity != ErrorSeverity.None)
            {
                // Some non-critical errors were found while loading project, for example missing recipe or analysis warnings
                foreach (var (error, _) in errorCollector.GetArrErrors())
                {
                    Console.Error.WriteLine(error);
                }
                
            }
            Console.WriteLine(">> Writing mod json...");
            // To confirm project loading, enumerate all objects
            foreach (var obj in Database.recipesAndTechnologies.all)
            {   
                //Console.WriteLine(obj.locName);
            }
            Console.WriteLine("Number of recipes found is: " + Database.recipes.all.Length);
            Console.WriteLine(">> Serializing stuff");
            /**
            var settings = new JsonSerializerSettings
            {
                ReferenceLoopHandling = ReferenceLoopHandling.Ignore,
                MaxDepth = 2,
                //IgnoreReadOnlyProperties = true,
                //WriteIndented = true
            }; **/

            var options = new JsonSerializerOptions
            {
                //
                //ReferenceHandler = ReferenceHandler.IgnoreCycles,
                //DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingDefault,
                NumberHandling = JsonNumberHandling.AllowNamedFloatingPointLiterals,
                WriteIndented = true,
                MaxDepth = 10
            };

            var sciencepacks = new List<Object>();
            //            foreach (var obj in Database.allSciencePacks)
            //           {
            //              sciencepacks.Add(tech(obj));   
            //         }
            foreach (var e in Database.entities.all)
            {
              //  Console.WriteLine("" + e);

               var  z2342 = 234;
            }
            
            foreach (var e in Database.technologies.all)
            {
               // Console.WriteLine("" + e);
                var zzz = 234;
            }

               foreach (var e in Database.recipes.all)
            {
                //var pr = ;
                //var tp = ;
                if (!e.IsAccessible())
                {
                    Console.WriteLine(e);

                }
                if (e.typeDotName == "Recipe.algae-farm")
                {
                    Console.WriteLine("" + e);
                    break;
                }

                



                //var js = JsonSerializer.Serialize(e_flat, options);
                //Console.WriteLine(js);
                //File.WriteAllText("dumped.json", js);
                //Console.WriteLine(e);
                //break;
            }
            foreach (var g in Database.goods.all)
            {
                if (g.typeDotName == "Item.used-up-thorium-fuel-cell")
                {
                    Console.WriteLine("" + g);
                    break;
                }
            }


            var x = new {   
                        sciencepacks = flattt(Database.allSciencePacks, "sciencepacks"), 
                           technologies = flattt(Database.technologies.all, "technologies"),
                           recipes_and_technology = flattt(Database.recipesAndTechnologies.all, "rt"),
                           goods = flattt(Database.goods.all, "goods"),
                //                           items = flattt(Database.items.all),
                            entities = flattt(Database.entities.all, "entities"),
                            recipes = flattt(Database.recipes.all, "recipes"),
            };
            //Database.goods.all
//            Database.items.all


            string json = JsonSerializer.Serialize(x, options);
            Console.WriteLine(">> Dumping json to stdout..");
            if (!debug) { 
                Console.WriteLine(json);
            }
            //File.WriteAllText("dumped.json", json);

        }
        public static List<object> flattt(IEnumerable<object> enm, string name)
        {
            Console.WriteLine("Flattening...");

            var sciencepacks = new List<Object>();
            foreach (var obj in enm)
            {
                sciencepacks.Add(tech(obj, name));
            }
            return sciencepacks;
        }
        public static Object tech(object obj, string fname, int cur_level=0, int max_level=1)
        {
            IDictionary<string, Object> dd = new Dictionary<string, Object>();    
            bool had_properties = false;

            List<object> objectList = obj.GetType().GetProperties().Cast<object>()
                .Concat(obj.GetType().GetFields().Cast<object>())
                .ToList();
            bool simplify = cur_level >= max_level;

            int next_level = cur_level + 1;
            foreach (PropertyInfo prop in obj.GetType().GetProperties())
            {
                string fname_next = fname;
                var type = Nullable.GetUnderlyingType(prop.PropertyType) ?? prop.PropertyType;
                if(type == typeof(System.Type))
                {
                    continue; // Unclear why but let's go. 
                }

                var v = prop.GetValue(obj, null);
               
                var is_ingredients = false;
                //Console.WriteLine("> " + prop.Name);

                if(prop.Name == "ingredients" && cur_level == 0)
                {
                    is_ingredients = true;             
                }
                // Expand some fields a bit extra...
                //int next_level = 1000;
                if ((fname == "technologies" || fname == "recipes") && prop.Name == "ingredients")
                {
                    simplify = false;
                    next_level = cur_level;
                }
                else if (fname == "recipes" && (prop.Name == "products" || prop.Name == "technologyUnlock"))
                {
                    fname_next = "recipes-df";
                    //max_level = 2;
                                        simplify = false;
                                        next_level = cur_level;
                    //next_level = cur_level + 1;
                }
                else
                {
                    next_level = cur_level + 1;
                }


                //Console.WriteLine(cur_level + " " + simplify + " " + max_level);
                if (cur_level > max_level && !simplify)
                {
                    Console.WriteLine("This cannot be. ");
                }
                if (v == null)
                {
                   // do nothing.
                }
                else if (v.GetType().IsArray == true || type == typeof(System.Collections.Generic.List<YAFC.Model.Fluid>)) {
                    if (!simplify) { 
                        List <Object> vv = new List<Object>();
                        IEnumerable enumerable = v as IEnumerable;
                        foreach (var e in enumerable)
                        {
                            var et = tech(e, fname_next, next_level, max_level);
                            if (is_ingredients) {
                                // Console.WriteLine(obj + " " + e + " " + et);
                            }

                            vv.Add(et);
                        }
                        dd.Add(prop.Name, vv);
                    }
                }
                else if (type == typeof(string) || type == typeof(bool)){                                     
                    dd.Add(prop.Name, v);
                }
                else if (type == typeof(System.Int32)
                    || type == typeof(System.Single)
                    )
                {                    
                    dd.Add(prop.Name, v);
                }
                else if (//type == typeof(YAFC.Model.FactorioId)
                   // || type == typeof(YAFC.Model.RecipeFlags)
                   // || type == typeof(YAFC.UI.Icon)
                   // || type == typeof(YAFC.Model.UnitOfMeasure)
                  //  || type == typeof(YAFC.Model.FactorioObjectSpecialType)
                  //  || type == typeof(YAFC.Model.FactorioObject)
                   // || type == typeof(YAFC.Model.Entity)
                   // || type == typeof(YAFC.Model.ModuleSpecification)
                   // || type == typeof(YAFC.Model.AllowedEffects)
                  //  || type == typeof(YAFC.Model.EntityEnergy)
                 //   || type == typeof(YAFC.Model.EntityEnergyType)
                     type == typeof(YAFC.Model.TemperatureRange)
                //    || type == typeof(YAFC.Model.Fluid)
                    )
                                {
                    //if (!simplify)
                    //{
                    TemperatureRange tr = (YAFC.Model.TemperatureRange)v;
                    
                        dd.Add(prop.Name, new {min=tr.min, max=tr.max} );
                    //}
                }
                else if (type == typeof(YAFC.Model.FactorioId)
                    || type == typeof(YAFC.Model.RecipeFlags)
                    || type == typeof(YAFC.UI.Icon)
                    || type == typeof(YAFC.Model.UnitOfMeasure)
                    || type == typeof(YAFC.Model.FactorioObjectSpecialType)
                    || type == typeof(YAFC.Model.FactorioObject)
                    || type == typeof(YAFC.Model.Goods)
                    || type == typeof(YAFC.Model.Entity)
                    || type == typeof(YAFC.Model.ModuleSpecification)
                    || type == typeof(YAFC.Model.AllowedEffects)
                    || type == typeof(YAFC.Model.EntityEnergy)
                    || type == typeof(YAFC.Model.EntityEnergyType)
                    || type == typeof(YAFC.Model.TemperatureRange)
                    || type == typeof(YAFC.Model.Item)
                    || type == typeof(YAFC.Model.Fluid)                    
                    ){
                    if (!simplify)
                    {
                        dd.Add(prop.Name, tech(v, fname_next, next_level, max_level));
                    }
                }               
                else
                {
                    Console.WriteLine("Not found!");
                    Console.WriteLine(prop.Name + " " + type);
                }

                if(prop.Name == "amount")
                {
                    Console.WriteLine(prop.Name + " " + v + " simplify " + simplify);
                    var a = 234;

                }
                had_properties = true;
            }
            foreach (FieldInfo prop in obj.GetType().GetFields())
            {
                var type = Nullable.GetUnderlyingType(prop.FieldType) ?? prop.FieldType;
                var v = prop.GetValue(obj);


                if (type == typeof(System.Int32)
                    || type == typeof(System.Single)
                    || type == typeof(string) || type == typeof(bool)
                    )
                {
                    dd.Add(prop.Name, v);
                }
                else
                {
                    if (!simplify)
                    {
                        dd.Add(prop.Name, tech(v, fname, next_level, max_level));
                    }
                }
                had_properties = true;
            }

            if (!had_properties)
            {
               return obj;
            }
            return dd;

        }
        
        private class ConsoleProgressReport : IProgress<(string, string)>
        {
            public void Report((string, string) value)
            {
                Console.WriteLine(value.Item1 +"  -  " + value.Item2);
            }
        }
    }
}