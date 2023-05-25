import json, os
from discord.ext import commands
from discord.ext.commands import has_permissions
import discord
import asyncio as asy
import random
from mcstatus import JavaServer as mc
import socket


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


    
def main():
    try:
        if os.path.exists('config.json'):
            with open('config.json', encoding='utf-8') as f:
                config_data = json.load(f)
        else:
            template = {'prefix':'#','token':"", 'palabrasbaneadas': [], 'mcservers':[]}
            with open('config.json','w', encoding='utf-8') as f:
                json.dump(template,f, ensure_ascii=False)
        
        #Variables globales
        
        palabras_baneadas = config_data["palabrasbaneadas"]  
        prefix = config_data["prefix"]
        token = config_data["token"]
        intents = discord.Intents.all()
        intents.presences = True
        intents.members = True
        bot = commands.Bot(command_prefix = prefix, intents = intents, description = "Hi! Im Anaconda from M.O.Dev.")
        mesajes_groserias = ["ha dicho una grosería. Meenlo en la boca", "mas cuidado, a algún loco se le va a zafar un tornillo.",
                             "este es un servidor decente, maldit@ boquisuci@", "respeta.", "una groseria mas y te lavamos la boca con jabon rey",
                             "te queremos mucho, pero eres muy groser@.", "basta de decir groserias maldit@ pesad@."]
        
        mcservers = config_data["mcservers"]
        
        #ReactionList
        reaction_numbers = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣""#️⃣","*️⃣","🔟","0️⃣"]
        
        #Variables de tiempo
        tiempo_corto     = 10
        tiempo_medio     = 30
        tiempo_largo     = 60
        tiempo_muy_largo = 180
        
        #------------------------------------------------------------------------------------------------------------------------------------------
        #Functions
        #------------------------------------------------------------------------------------------------------------------------------------------
        def is_before_element(element, index, lst):
            if element in lst[:index]:
                return True
            else:
                return False
        
        async def delete_after_time(ctx, cont_numb, mensaje):
            await asy.sleep(tiempo_medio)  # Esperar 30 segundos
            try:
                mensaje = await ctx.fetch_message(mensaje.id)  # Obtener el mensaje actualizado
                reacciones = mensaje.reactions
                cantidad_reacciones = 0          
                for reaccion in reacciones:
                    cantidad_reacciones += reaccion.count
                    print(cantidad_reacciones)      
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
            try:
                return tipo_dato(dato), True
            except (ValueError, TypeError):
                return dato, False
        #------------------------------------------------------------------------------------------------------------------------------------------
        #Init bot
        #------------------------------------------------------------------------------------------------------------------------------------------
        @bot.event
        async def on_ready():
            bot.comando1_message_id = 0  # Inicializar el atributo comando1_message_id
            bot.comando2_message_id = 0  # Inicializar el atributo comando2_message_id
            await bot.change_presence(activity=(discord.Game(name="#help")))
        
        
        #------------------------------------------------------------------------------------------------------------------------------------------
        #Comandos de moderación
        #------------------------------------------------------------------------------------------------------------------------------------------
        #-Banear palabra del servidor
        @has_permissions(administrator=True)
        @bot.command(help="Banear palabra del servidor")
        async def banword(ctx, palabra):
            if palabra.lower() in palabras_baneadas:
                msg = await ctx.send(embed = Crear_Respuesta(f"Ya está baneada esta palabra.",None).enviar)
                await asy.sleep(tiempo_corto)
                await msg.delete()
            else:
                palabras_baneadas.append(palabra.lower())
                with open('config.json', 'r+', encoding="utf-8") as f:
                    datos = json.load(f)
                    datos['palabrasbaneadas'] = palabras_baneadas
                    f.seek(0)
                    f.write(json.dumps(datos))
                    f.truncate()
                respuesta = Crear_Respuesta('Admin Info',f'Palabra baneada del servidor correctamente: {palabra}')
                msg = await ctx.reply(embed = respuesta.enviar)
                await asy.sleep(tiempo_corto)
                await msg.delete()
                
        
        #-Quitar ban a la  palabra
        @has_permissions(administrator=True)
        @bot.command(help = "Quitar la palabra baneada del servidor")
        async def unbanword(ctx, palabra):
            if palabra.lower() in palabras_baneadas:
                palabras_baneadas.remove(palabra.lower())
                with open('config.json','r+',encoding="utf-8") as f:
                    datos = json.load(f)
                    datos['palabrasbaneadas'] = palabras_baneadas
                    f.seek(0)
                    f.write(json.dumps(datos))
                    f.truncate()
                respuesta = Crear_Respuesta('Admin Info',f"Palabra desbaneada correctamente:) {palabra}")
                msg = await ctx.send(embed = respuesta.enviar)
                await asy.sleep(tiempo_corto)
                await msg.delete()
            else:
                respuesta = Crear_Respuesta('Admin Info', 'Esa palabra no está baneada aún.')
                msg = await ctx.reply(embed = respuesta.enviar)
                await asy.sleep(tiempo_corto)
                await msg.delete()
                

        #------------------------------------------------------------------------------------------------------------------------------------------
        #comandos
        #------------------------------------------------------------------------------------------------------------------------------------------     
        @bot.command(name="operar", help="Opera varios numeros")
        async def operar(ctx, cadena:str):
            try:
                res = eval(cadena)
                respuesta = Crear_Respuesta(f'Resultado: {res}', None)              
                await ctx.reply(embed = respuesta.enviar)

            except:
                respuesta = Crear_Respuesta(f"Pilas que ahí hay un carácter no numérico",None)
                await ctx.reply(embed = respuesta.enviar)
                
                 
        @bot.command(name="server", help="Obtén el estado de los servidores de minecraft!")
        async def server(ctx):           
            cont_numb = 0
            msg_list = []
            for server in mcservers:
                msg_list.append(f"{reaction_numbers[cont_numb]}  {server[0]}")
                cont_numb+=1
            msg_list_formatted = '\n'.join(msg_list)
            
            respuesta = Crear_Respuesta("Servidores de Minecraft",f"Reacciona para ver su estado: \n\n {msg_list_formatted}")
            mensaje = await ctx.send(embed = respuesta.enviar)  
            cont_numb = 0
            for server in mcservers:
                await mensaje.add_reaction(reaction_numbers[cont_numb])
                cont_numb+=1  
                
            author_id = ctx.author.id
            bot.comando1_author_id = author_id
            bot.comando1_message_id = mensaje.id
            bot.comando1_reaction_limit = cont_numb
            
            await delete_after_time(ctx, cont_numb, mensaje)
              
        #<--Test permisions
        @has_permissions(administrator = True)  
        @bot.command(name="delserver", help="Elimina algún servidor de minecraft")
        async def delserver(ctx):
            cont_numb = 0
            msg_list = []
            
            for server in mcservers:
                msg_list.append(f"{reaction_numbers[cont_numb]}  {server[0]}")
                cont_numb += 1
            msg_list_formatted = '\n'.join(msg_list)
                
            cont_numb = 0
            respuesta = Crear_Respuesta("Servidores de Minecraft", f"Reacciona para borrar un servidor:\n\n{msg_list_formatted}")
            mensaje = await ctx.send(embed=respuesta.enviar)
            for server in mcservers:
                await mensaje.add_reaction(reaction_numbers[cont_numb])
                cont_numb += 1
                
            author_id = ctx.author.id
            bot.comando2_author_id = author_id
            bot.comando2_message_id = mensaje.id
            bot.comando2_reaction_limit = cont_numb 

            await delete_after_time(ctx, cont_numb, mensaje)
                       
        #Añadir Servidor
        @has_permissions(administrator=True)
        @bot.command(name="addserver", help="Añade un servidor a lista.")
        async def addserver(ctx, ipserver="nfpj", port=-1, admins="n"):
            ban = -1  
            errors = [f"El formato para añadir servidores es:\n Si es un servidor público: \n-> #addserver <ip_del_servidor> <port (opcional)> <admins (opcional SIN ESPACIOS)> \n\nSi el servidor es tuyo, de tus amigos o privado:\n-> #addserver <ip_del_servidor> <puerto> <admins(opcional SIN ESPACIOS)> \n\nLos campos opcionales pueden ser dejados en blanco.",
                      "El servidor ya está registrado. No se añadirá."]  
               
            if ipserver == "nfpj":
                print(f"No ingresó un servidor")             
                ban = 0 
                
            print(ipserver, port, admins)
            for server in mcservers:
                if server[0] == ipserver:
                    ban = 1
                    break
            
            if ban == -1:
                
                ipserver, state = tryParse(ipserver, str)
                if not state:
                    ipserver = "n"
                else:
                    ipserver = str(ipserver).strip() if str(ipserver).strip() != "" else "n"
            
                port, state  = tryParse(port,int)    
                if not state:
                    port = -1

                admins, state = tryParse(admins, str)
                if not state: 
                    admins= "n"
                else:
                    admins = str(admins).strip() if str(admins).strip() != "" and not str(admins).strip().isdigit() and str(admins).strip() != "n" else "n"
                                

                new_server = [ipserver, port, admins]
                mcservers.append(new_server)
                
                with open('config.json', 'r+', encoding='utf-8') as f:
                    datos = json.load(f)
                    datos['mcservers'] = mcservers
                    f.seek(0)
                    f.write(json.dumps(datos))
                    f.truncate()
                respuesta = Crear_Respuesta("Admin Info Temporal", f"Servidor añadido correctamente")
                msg = await ctx.reply(embed = respuesta.enviar)
                await asy.sleep(tiempo_medio)
                await msg.delete()  
                        
            else:
                respuesta = Crear_Respuesta("Advertencia", errors[ban])     
                await ctx.send(embed = respuesta.enviar)
                   
        #------------------------------------------------------------------------------------------------------------------------------------------
        #Etiquetas de los comandos
        #------------------------------------------------------------------------------------------------------------------------------------------
        operar.category = 'Misce'
        server.category = 'Minecraft'
        addserver.category = 'Minecraft'
        delserver.category = 'Minecraft'
        banword.category = 'Moderation'
        unbanword.category = 'Moderation'
        
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
            
                   
        #------------------------------------------------------------------------------------------------------------------------------------------
        #eventos
        #------------------------------------------------------------------------------------------------------------------------------------------
        reacted_message_ids = set()
        @bot.event
        async def on_raw_reaction_add(payload):
            # Obtener el ID del usuario y el ID del canal
            user_id    = payload.user_id
            channel_id = payload.channel_id
            message_id = payload.message_id

            # Verificar si el autor de la reacción no es el bot
            if user_id != bot.user.id:
                channel = await bot.fetch_channel(channel_id)
            
                # Verificar si la reacción fue añadida al mensaje correcto utilizando el ID del mensaje.
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
                                
                            except socket.timeout as err:
                                alternative = f"Puerto: {server_port}" if server_port != -1 else f"Puerto: No se asignó puerto"
                                respuesta = Crear_Respuesta(f"Tiempo de espera agotado.",f"Muy probablemente la dirección de tu servidor es inexistente o el puerto es erroneo.\n Te invitamos a verificar la dirección y el puerto en caso de que lo hayas asignado.\nServidor {server_address}\n{alternative}\nLog ->{err}")
                                await channel.send(embed = respuesta.enviar)
                            except ConnectionRefusedError as err:
                                respuesta = Crear_Respuesta(f"No se pudo establecer conexión a {actual_server[0]}",f"Error enviado por tu host -> {err}")
                                await channel.send(embed = respuesta.enviar)
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
                    
                        respuesta = Crear_Respuesta('Admin Info',f"Servidor borrado correctamente.")
                        await channel.send(embed = respuesta.enviar)
                else:
                    # La reacción se hizo en otro mensaje
                    # No se realiza ninguna acción
                    pass
        
        @bot.event
        async def on_message(message):
            message_content = message.content.lower()
            message_content = message_content.split(' ')
            respuesta = None  # Valor predeterminado de la variable respuesta
            
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

        bot.run(token)
    except (Exception) as error:
        print(error)
        
        
if __name__ == '__main__':
    main()