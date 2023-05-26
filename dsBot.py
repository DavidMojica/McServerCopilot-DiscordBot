#------------------------------------------------------------------------------------
#Imports
#------------------------------------------------------------------------------------
#Sys - Python libs
import json, os
import random
import asyncio as asy
import socket
#Discord Libs
from discord.ext import commands
from discord.ext.commands import has_permissions
import discord
#Minecraft Libs
from mcstatus import JavaServer as mc #Proximamente se trabajará con Bedrock Server


#------------------------------------------------------------------------------------
#Clases
#------------------------------------------------------------------------------------
class Crear_Respuesta():
    def __init__(self, title, content):
        self.title = title
        self.content = content
        self.respuesta = discord.Embed(
            title = self.title,
            description=self.content,
            colour= int("FFFFFF",16)       
        )
    @property
    def enviar(self):
        return self.respuesta


#------------------------------------------------------------------------------------
#Codigo
#------------------------------------------------------------------------------------
def main():
    #------------------------------------------------------------------------------------
    #Operaciones iniciales con el archivo config.json
    #------------------------------------------------------------------------------------
    try:
        #Intenta llamar al archivo config.json
        if os.path.exists('config.json'):
            with open('config.json', encoding='utf-8') as f:
                config_data = json.load(f)
        #Si no existe, crea el archivo con los datos preestablecidos en la variable template
        else:
            template = {'prefix':'#','token':"", 'palabrasbaneadas': [], 'mcservers':[]}
            with open('config.json','w', encoding='utf-8') as f:
                json.dump(template,f, ensure_ascii=False)
        
        #Bot Config
        prefix            = config_data["prefix"]
        token             = config_data["token"]
        intents           = discord.Intents.all()
        intents.presences = True
        intents.members   = True
        bot = commands.Bot(command_prefix = prefix, intents = intents, description = "Hi! Im Anaconda from M.O.Dev.")
        
        #------------------------------------------------------------------------------------
        #Listas
        #------------------------------------------------------------------------------------
        #Listas desde config.json
        palabras_baneadas = config_data["palabrasbaneadas"]  
        mcservers         = config_data["mcservers"]
        
        #Listas
        mesajes_groserias = ["ha dicho una grosería. Meenlo en la boca", "mas cuidado, a algún loco se le va a zafar un tornillo.",
                             "este es un servidor decente, maldit@ boquisuci@", "respeta.", "una groseria mas y te lavamos la boca con jabon rey",
                             "te queremos mucho, pero eres muy groser@.", "basta de decir groserias maldit@ pesad@."]
        message_headers = ["Admin Info","Servidores de Minecraft"]
        #ReactionList
        reaction_numbers = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣""#️⃣","*️⃣","🔟","0️⃣"]
              
        #------------------------------------------------------------------------------------
        #Sets
        #------------------------------------------------------------------------------------
        reacted_message_ids = set() #Set usado para añadir los mensajes ya reaccionados para que no hagan nada si vuelven a ser reaccionados.
        
        #Variables de tiempo
        tiempo_corto     = 10
        tiempo_medio     = 30
        tiempo_largo     = 60
        tiempo_muy_largo = 180
        
        #------------------------------------------------------------------------------------
        # #Functions
        #------------------------------------------------------------------------------------
        def is_before_element(element, index, list):
            """
            Esta función verifica que el elemento esté en la lista y que esté antes del índice especificado o en el índice mismo.
            
            Parámetros:
            element (any) : Elemento a buscar en la lista.
            index   (int) : Posición. Se buscará desde la posicion hacia atrás.
            list    (list): Lista que se desea utilizar.
            
            Retorna: (bool)
            True : Si el elemento está en el índice especificado o antes.
            False: Si el elemento está después del indice especificado o no está en la lista.
            
            Ejemplo:
            lista = [1,2,"a","b"]
            >>>is_before_element("a",1,lista)
            False
            
            >>>is_before_element("a",3,lista)
            True
            """
            if element in list[:index]:
                return True
            else:
                return False
        
        async def delete_after_time(ctx, cont_numb, mensaje):
            """
            Esta función borra el mensaje emitido por un bot o usuario en un periodo de tiempo si no se ha reaccionado al mismo.
            
            Parámetros:
            ctx(discord object - context)     : Contexto del mensaje.
            cont_numb(int)                    : Numero de reacciones que contiene el mensaje.
            mensaje(discord object - message) : Mensaje en específico.
            """
            await asy.sleep(tiempo_medio)  # Esperar 30 segundos
            try:
                mensaje = await ctx.fetch_message(mensaje.id)  # Obtener el mensaje actualizado
                reacciones = mensaje.reactions
                cantidad_reacciones = 0          
                for reaccion in reacciones:
                    cantidad_reacciones += reaccion.count
                if cantidad_reacciones == cont_numb:
                    await mensaje.delete()
                    respuesta = Crear_Respuesta("Alerta", "Mensaje eliminado por inactividad.")
                    alert = await ctx.reply(embed = respuesta.enviar)
                    await asy.sleep(tiempo_corto)
                    await alert.delete()
                
            except discord.NotFound:
                # El mensaje se ha eliminado, manejar el caso en consecuencia
                respuesta = Crear_Respuesta("Error","El mensaje ha sido eliminado por fuerzas externas.")
                alert = await ctx.send(embed = respuesta.enviar)
                await asy.sleep(tiempo_corto)
                await alert.delete()
                           
        def tryParse(dato, tipo_dato):
            """
            Esta función intenta convertir el dato en el tipo de dato solicitado y devuelve el tipo de dato ya convertido si la conversion es exitosa, también devuelve True. En caso contrario, devuelve el dato sin convertir y False.
            
            Parámetros:
            dato (any)           : El dato que se quiere convertir.
            tipo_dato(data_type) : Tipo de dato al que se quiere convertir.
            
            Retorna: (any),(bool)
            (tipo_dato)Any, True : Si el elemento ha sido convertido con exito.
            Any, False           : Si el elemento no logró ser convertido.
            
            Ejemplo:
            nombre = "42asd"
            edad = "1000"
            
            >>>nombre, confirmation = tryParse(nombre, int)
            nombre: "42asd", confirmation = False
            
            >>>nombre, confirmation = tryParse(nombre, str)
            nombre = "42asd", confirmation = True
            
            >>>edad, confirmation = tryParse(edad, int)
            edad = 1000, confirmarion = True
            """
            try:
                return tipo_dato(dato), True
            except (ValueError, TypeError):
                return dato, False
        #------------------------------------------------------------------------------------
        #Inicialización del bot - Init bot
        #------------------------------------------------------------------------------------        
        @bot.event
        async def on_ready():
            bot.comando1_message_id = 0  # Inicializar el atributo comando1_message_id
            bot.comando2_message_id = 0  # Inicializar el atributo comando2_message_id
            await bot.change_presence(activity=(discord.Game(name="#help"))) #Ponerle actividad al bot.
        
        #------------------------------------------------------------------------------------
        #Comandos
        #------------------------------------------------------------------------------------
        
        #---Comandos de moderación---#
        #-Banear palabra del servidor
        @has_permissions(administrator=True) #Verificar si el usuario que está llamando al comando es admin o no.
        @bot.command(name ="banword",help="Banear palabra del servidor.")
        async def banword(ctx, palabra):    
            #Convierte los carácteres de la palabra a minúsculas y las busca en la lista de palabras baneadas.
            if palabra.lower() in palabras_baneadas: #Se comprueba si esa palabra ya está baneada.
                msg = await ctx.send(embed = Crear_Respuesta(f"Ya está baneada esta palabra.",None).enviar)
                await asy.sleep(tiempo_corto)
                await msg.delete()                   #El mensaje se borra despues de un tiempo.
            else:                                    #Si no está baneada, se crea la palabra y se actualiza el archivo json.   
                palabras_baneadas.append(palabra.lower())
                with open('config.json', 'r+', encoding="utf-8") as f:
                    datos = json.load(f)
                    datos['palabrasbaneadas'] = palabras_baneadas
                    f.seek(0)
                    f.write(json.dumps(datos))
                    f.truncate()
                respuesta = Crear_Respuesta(message_headers[0],f'Palabra baneada del servidor correctamente: {palabra}')
                msg = await ctx.reply(embed = respuesta.enviar)
                await asy.sleep(tiempo_corto)
                await msg.delete()                   #El mensaje se borra despues de un tiempo.
                
        
        #Quitar ban a la  palabra
        @has_permissions(administrator=True)
        @bot.command(name="unbanword",help = "Quitar ban a la palbra del servidor")
        async def unbanword(ctx, palabra):
            #Convierte los carácteres de la palabra a minúsculas y las busca en la lista de palabras baneadas.
            if palabra.lower() in palabras_baneadas:            #Comprueba que la palabra sí esté en la lista de palabras baneadas
                palabras_baneadas.remove(palabra.lower())
                with open('config.json','r+',encoding="utf-8") as f:
                    datos = json.load(f)
                    datos['palabrasbaneadas'] = palabras_baneadas
                    f.seek(0)
                    f.write(json.dumps(datos))
                    f.truncate()
                respuesta = Crear_Respuesta(message_headers[0],f"Palabra desbaneada correctamente:) {palabra}")
                msg = await ctx.send(embed = respuesta.enviar)
                await asy.sleep(tiempo_corto)
                await msg.delete()
            else:                                               #Si no está, se devuelve un mensaje de error.
                respuesta = Crear_Respuesta(message_headers[0], 'Esa palabra no está baneada aún.')
                msg = await ctx.reply(embed = respuesta.enviar)
                await asy.sleep(tiempo_corto)
                await msg.delete()
                

        #------------------------------------------------------------------------------------
        #comandos miscelanea
        #------------------------------------------------------------------------------------  
        #Realiza operaciones matemáticas
        @bot.command(name="operar", help="Realiza operaciones matemáticas básicas.")
        async def operar(ctx, cadena:str):
            try:
                res = eval(cadena)
                respuesta = Crear_Respuesta(f'Resultado: {res}', None)              
                await ctx.reply(embed = respuesta.enviar)

            except:
                respuesta = Crear_Respuesta(f"Pilas que ahí hay un carácter no numérico",None)
                await ctx.reply(embed = respuesta.enviar)

        #Muestra la ayuda de los comandos de una forma distinta
        @bot.command(name='helps', help='Muestra la ayuda del bot')
        async def helps(ctx, category=None):
            command_list = bot.commands
            if not category:
                # Si no se proporciona una categoría, mostrar todos los comandos
                embed = discord.Embed(title='Ayuda del Bot', color=discord.Color.blue())
                for command in command_list:
                    embed.add_field(name=command.name, value=command.help, inline=False)
                await ctx.send(embed=embed)
            else:
                # Mostrar comandos por categoría específica
                embed = discord.Embed(title=f'Ayuda de la categoría {category}', color=discord.Color.blue())
                for command in command_list:
                    if getattr(command, 'category', None) == category:
                        embed.add_field(name=command.name, value=command.help, inline=False)
                await ctx.send(embed=embed)     
                
        #------------------------------------------------------------------------------------
        #comandos del servidor de Minecraft
        #------------------------------------------------------------------------------------  
        #Verificar el estado de algún servidor de minecraft previamente añadido a la lista.        
        @bot.command(name="server", help="Obtén el estado de los servidores de minecraft!")
        async def server(ctx):           
            cont_numb = 0       #Contador. Será usado para crear la lista de servidores y para añadir reacciones al mensaje, además para hacer validaciones.
            msg_list = []       #Se crea una lista para después mostrar la lista de servidores de forma ordenada.
            for server in mcservers:
                msg_list.append(f"{reaction_numbers[cont_numb]}  {server[0]}")
                cont_numb+=1
            msg_list_formatted = '\n'.join(msg_list)         #Ordenamos la lista con un formato de lista valga la redundancia.
            cont_numb = 0
            respuesta = Crear_Respuesta(message_headers[1],f"Reacciona para ver su estado: \n\n {msg_list_formatted}")
            mensaje = await ctx.send(embed = respuesta.enviar)  
            for server in mcservers:
                await mensaje.add_reaction(reaction_numbers[cont_numb])
                cont_numb+=1               
            author_id = ctx.author.id                        #Obtenemos el autor del comando.
            bot.comando1_author_id = author_id               #Establecemos como propiedad del mensaje al autor del comando.
            bot.comando1_message_id = mensaje.id             #Establecemos como propiedad el id del mensaje.
            bot.comando1_reaction_limit = cont_numb          #Establecemos como propiedad la cantidad de reacciones que inicialmente tiene el mensaje.
            await delete_after_time(ctx, cont_numb, mensaje) #Llamamos a la función encargada de borrar el mensaje si no se reacciona a él en un tiempo determinado.
              
        #Borrar un servidor de minecraft previamente añadido a la lista.
        @has_permissions(administrator = True)      #Verificar si el usuario que está llamando al comando es admin o no.
        @bot.command(name="delserver", help="Elimina algún servidor de minecraft")
        async def delserver(ctx):
            cont_numb = 0       #Contador. Será usado para crear la lista de servidores y para añadir reacciones al mensaje, además para hacer validaciones.
            msg_list = []       #Se crea una lista para después mostrar la lista de servidores de forma ordenada.
            for server in mcservers:
                msg_list.append(f"{reaction_numbers[cont_numb]}  {server[0]}")
                cont_numb += 1
            msg_list_formatted = '\n'.join(msg_list)         #Ordenamos la lista con un formato de lista valga la redundancia.
            cont_numb = 0
            respuesta = Crear_Respuesta(message_headers[1], f"Reacciona para borrar un servidor:\n\n{msg_list_formatted}")
            mensaje = await ctx.send(embed=respuesta.enviar)
            for server in mcservers:
                await mensaje.add_reaction(reaction_numbers[cont_numb])
                cont_numb += 1
            author_id = ctx.author.id                        #Obtenemos el autor del comando.
            bot.comando2_author_id = author_id               #Establecemos como propiedad del mensaje al autor del comando.
            bot.comando2_message_id = mensaje.id             #Establecemos como propiedad el id del mensaje.
            bot.comando2_reaction_limit = cont_numb          #Establecemos como propiedad la cantidad de reacciones que inicialmente tiene el mensaje.    
            await delete_after_time(ctx, cont_numb, mensaje) #Llamamos a la función encargada de borrar el mensaje si no se reacciona a él en un tiempo determinado.
                       
        #Añadir Servidor servidor a la lista de servidores del servidor.
        @has_permissions(administrator=True)
        @bot.command(name="addserver", help="Añade un servidor a lista.") 
        async def addserver(ctx, ipserver="nfpj", port=-1, admins="n"): #Se reciben todos los parámetros de forma opcional.
            ban = -1  
            errors = [f"El formato para añadir servidores es:\n Si es un servidor público: \n-> #addserver <ip_del_servidor> <port (opcional)> <admins (opcional SIN ESPACIOS)> \n\nSi el servidor es tuyo, de tus amigos o privado:\n-> #addserver <ip_del_servidor> <puerto> <admins(opcional SIN ESPACIOS)> \n\nLos campos opcionales pueden ser dejados en blanco.",
                      "El servidor ya está registrado. No se añadirá.","Ya hay demasiados servidores en la lista. Borre alguno. Próximamente se añadirán más espacios."]  
            #Si no se ingresó un servidor, ban toma el valor de 0.              
            if ipserver == "nfpj":
                ban = 0 
            #Si el servidor ingresado se encuenta en la lista de servidores, ban toma el valor de 1.
            for server in mcservers:
                if server[0] == ipserver:
                    ban = 1
                    break
            #Verificar que la lista de servidores no sea demasiado grande.
            if len(mcservers) >= 8:
                ban = 2
            
            #Si pasó estas dos validaciones, ban sigue con su valor inicial y puede entrar al condicional.
            if ban == -1:
                #Intenta convertir la ip del servidor a cadena de texto. Si por alguna razón no puede, se le asigna el valor de "n"
                ipserver, state = tryParse(ipserver, str)
                if not state:
                    ipserver = "n"
                else:
                    ipserver = str(ipserver).strip() if str(ipserver).strip() != "" else "n"
                #Intenta convertir el puerto a un numero entero, si no puede, el puerto toma el valor de -1.
                port, state  = tryParse(port,int)    
                if not state:
                    port = -1
                #Intenta convertir los admins a string. Si no puede, admins toma el valor de "n"
                admins, state = tryParse(admins, str)
                if not state: 
                    admins= "n"
                else:
                    admins = str(admins).strip() if str(admins).strip() != "" and not str(admins).strip().isdigit() and str(admins).strip() != "n" else "n"
                #Crea una lista con los datos del servidor y los agrega a la lista de servidores.
                new_server = [ipserver, port, admins]
                mcservers.append(new_server)
                #Abrimos el archivo json y lo preparamos para cargar la lista actualizada.
                with open('config.json', 'r+', encoding='utf-8') as f:
                    datos = json.load(f)
                    datos['mcservers'] = mcservers
                    f.seek(0)
                    f.write(json.dumps(datos))
                    f.truncate()
                respuesta = Crear_Respuesta(message_headers[0], f"Servidor añadido correctamente")
                #Mensaje temporal.
                msg = await ctx.reply(embed = respuesta.enviar)
                await asy.sleep(tiempo_medio)
                await msg.delete()  
                        
            else:
                respuesta = Crear_Respuesta("Error al añadir", errors[ban])     
                await ctx.send(embed = respuesta.enviar)         
                   
        #----------------------------------------------------------------------------------------------------------
        #eventos
        #----------------------------------------------------------------------------------------------------------
        #on raw reaction, constantemente está mirando si algún usuario reacionó a algún mensaje emitido por el bot
        @bot.event
        async def on_raw_reaction_add(payload):
            # Obtener el ID del usuario y el ID del canal
            user_id    = payload.user_id
            channel_id = payload.channel_id
            message_id = payload.message_id
            # Verificar si el autor de la reacción no es el bot
            if user_id != bot.user.id:
                channel = await bot.fetch_channel(channel_id)
                #Verificar si la reacción fue añadida al mensaje correcto utilizando el ID del mensaje.
                #Verificar si el mensaje no ha sido reaccionado antes.
                #Verificar si el autor del comando es quien reacciona al mensaje emitido por el bot.
                #if payload.message_id == bot.server_message_id:
                if message_id == bot.comando1_message_id and message_id not in reacted_message_ids and user_id == bot.comando1_author_id:
                    emoji = payload.emoji.name
                    #Verificar que el mensaje haya sido reaccionado con uno de los emojis permitidos.
                    try:                    
                        if is_before_element(emoji, bot.comando1_reaction_limit, reaction_numbers):
                            reacted_message_ids.add(message_id)
                            position       = reaction_numbers.index(emoji)
                            actual_server  = mcservers[position]
                            server_address = actual_server[0]
                            server_port    = actual_server[1] #Si no se asignó port      -> -1
                            server_admin   = actual_server[2] #Si no se asignaron admins -> "n"
                            try:
                                if not str(server_port).isdigit():
                                    server = mc(server_address, timeout=5)
                                else:
                                    server = mc(server_address, server_port, timeout=5)
                                status = server.status()
                                # Obtener los detalles del estado del servidor
                                version        = status.version.name
                                players_online = status.players.online
                                max_players    = status.players.max
                                latency        = status.latency
                                latency = round(latency, 1)
                                # Envía el mensaje con el estado del servidor 
                                if version.lower().__contains__('offline'):       
                                    alternative = "El servidor se encuentra apagado." if server_admin == "n" else f"El servidor se encuentra apagado.\nPuedes decirle al Admin: {server_admin} que lo encienda."
                                    respuesta = Crear_Respuesta(actual_server[2], alternative)
                                else: 
                                    alternative = actual_server[2] if actual_server[2] != "n" else actual_server[0]
                                    respuesta = Crear_Respuesta(alternative,f"Estado/Version: {version}\nJugadores en línea: {players_online}/{max_players}\nLatencia: {latency} ms")
                                await channel.send(embed= respuesta.enviar)
                            #Previene un error por exceso de tiempo de la solicitud.
                            except socket.timeout as err:
                                alternative = f"Puerto: {server_port}" if server_port != -1 else f"Puerto: No se asignó puerto"
                                respuesta = Crear_Respuesta(f"Tiempo de espera agotado.",f"Muy probablemente la dirección de tu servidor es inexistente o el puerto es erroneo.\n Te invitamos a verificar la dirección y el puerto en caso de que lo hayas asignado.\nServidor {server_address}\n{alternative}\nLog ->{err}")
                                await channel.send(embed = respuesta.enviar)
                            #Previene un error por conexión rechazada por parte del servidor al que se está intentado conectar.
                            except ConnectionRefusedError as err:
                                respuesta = Crear_Respuesta(f"No se pudo establecer conexión a {actual_server[0]}",f"Error enviado por tu host -> {err}")
                                await channel.send(embed = respuesta.enviar)
                            except UnicodeError as err:
                                respuesta = Crear_Respuesta(f"Ese no es un servidor",f"Babos@ error--> {err}")
                                await channel.send(embed = respuesta.enviar)
                            except socket.gaierror as err:
                                respuesta = Crear_Respuesta(f"Ese no es un servidor", f"gai --> {err}")
                    #Previene un error por buscar elemento fuera de los límites de la lista de servidores, suele ocurrir cuando abres la lista de servidores y la de borrar servidores al mismo tiempo, borras el ultimo servidor y luego lo buscas, así se genera este error.
                    except IndexError as err:
                                respuesta = Crear_Respuesta(f"Índice fuera de la lista",f"Ha intentado buscar un servidor que ya no existe.")
                                await channel.send(embed = respuesta.enviar)    
                    else:
                        pass
                elif message_id == bot.comando2_message_id and message_id not in reacted_message_ids and user_id == bot.comando2_author_id:
                    emoji = payload.emoji.name
                    #Verificar que el mensaje haya sido reaccionado con uno de los emojis permitidos.
                    if is_before_element(emoji, bot.comando2_reaction_limit, reaction_numbers):
                        reacted_message_ids.add(message_id)
                        position       = reaction_numbers.index(emoji)
                        del mcservers[position]
                        with open('config.json', 'r+', encoding='utf-8') as f:
                            datos = json.load(f)
                            datos['mcservers'] = mcservers
                            f.seek(0)
                            f.write(json.dumps(datos))
                            f.truncate()
                        respuesta = Crear_Respuesta(message_headers[0],f"Servidor borrado correctamente.")
                        await channel.send(embed = respuesta.enviar)
                else:
                    # La reacción se hizo en otro mensaje
                    # No se realiza ninguna acción
                    pass
        
        #on_message:Constantemente está analizando los mensajes que emiten los usuarios del servidor.
        @bot.event
        async def on_message(message):
            message_content = message.content.lower()
            message_content = message_content.split(' ')
            respuesta = None  # Valor predeterminado de la variable respuesta
            #Verificamos que el mensaje no esté en palabras baneadas.
            for palabrabaneada in palabras_baneadas:
                if palabrabaneada in message_content:
                    respuesta = Crear_Respuesta('Admin Message',f'{message.author} {mesajes_groserias[random.randint(0,len(mesajes_groserias))]}')
                    await message.reply(embed = respuesta.enviar)
                    await asy.sleep(tiempo_corto)
                    await message.delete()
                    break
            await bot.process_commands(message)
            if respuesta is None:
                pass 
        #Función para poner a "rodar" el bot.
        
        
        #------------------------------------------------------------------------------------
        #Etiquetas de los comandos - Not working yet
        #------------------------------------------------------------------------------------ 
        helps.category     = 'Misc' 
        operar.category    = 'Misc'
        server.category    = 'Minecraft'
        addserver.category = 'Minecraft'
        delserver.category = 'Minecraft'
        banword.category   = 'Moderation'
        unbanword.category = 'Moderation'
        
        bot.run(token)
    except (Exception) as error:
        print(error)
        
#Inicialización del programa.
if __name__ == '__main__':
    main()