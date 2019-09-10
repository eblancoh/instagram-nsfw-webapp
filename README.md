# Instagram NSFW Webapp

Este proyecto toma como bases las rutinas generadas bajo el proyecto [Instagram Scrapping: contribución **Departamento de Ideas Locas** Telefónica CDO](https://github.com/eblancoh/instagram-nsfw). Ver enlace para más detalles sobre esta primera PoC.

Haciendo uso del motor dessrrollado en la Prueba de Concepto anteriormente desarrollada, se ha creado una **Aplicación Web** sencilla usando [**Python Flask**](https://palletsprojects.com/p/flask/) y [**Bootstrap 3**](https://getbootstrap.com/docs/3.3/).

Resumen de uso
------------
En esta PoC se hace uso tanto de los siguientes WebDrivers para poder hacer el scrapping del contenido HTML:
* [ChromeDriver - WebDriver for Chrome](http://chromedriver.chromium.org/) 
* [GeckoDriver - WebDriver for Firefox](https://firefox-source-docs.mozilla.org/testing/geckodriver/)

Hay que incluir en el PATH las rutas en las que los drivers se encuentren. Para **Linux** basta con ejecutar:
```bash
$ export PATH=$PATH:/path/to/driver/chrome-driver
```
```bash
$ export PATH=$PATH:/path/to/driver/gecko-driver
```
Para añadir al PATH en **Windows**, se pueden seguir los [siguientes pasos](https://helpdeskgeek.com/windows-10/add-windows-path-environment-variable/).

### Levantar la página web en local

```python
python instagram_scrapper/app.py
```
Tras ejecutar este comando se levantará un servidor al que se puede acceder a través de la ruta:

```bash
http://localhost:5000/
```
Esto nos dirige a la página que nos permitirá lanzar el proceso de scraping del perfil privado.

IMAGEN

**Requisitos**: 
- Tener un perfil de Instagram. Las credenciales a usar se introducen en la página de login.
- El perfil a scrapear debe ser privado (objetivo).

Se lanza la búsqueda y se dan los siguientes pasos:
1. Se comprueba que se produce satisfactoriamente el login en Instagram.
2. Se comprueba que el usuario objetivo existe.
3. Se accede al perfil y se comienza a obtener a información en la que estamos interesados a través de Selenium y BeautifulSoup.

