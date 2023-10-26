import os

from celery import Celery

CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'

celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)


@jwt_required()
@app.route('/tasks/<int:id_task>', methods=['GET','DELETE'])
def task_by_id(id_task):
    print("** llegue -> ", request.method )
    if 'username' in session:
        
        if request.method == 'GET':
            task = FileConversionTask.query.filter_by(user_id=session['id_user'], id=id_task).first()

            if task is None:
                return 'Tarea no encontrada', 404  # Retorna un código 404 si la tarea no existe

            return render_template('id_tasks.html', username=session['id_user'], task=task)

        
        if request.method == 'DELETE':
            
            task = FileConversionTask.query.filter_by(user_id=session['id_user'], id=id_task).first()

            if task is None:
                return 'Tarea no encontrada', 404  # Retorna un código 404 si la tarea no existe
            
            # Elimina el archivo original y convertido del servidor
            if os.path.exists(task.original_filepath):
                os.remove(task.original_filepath)
            if os.path.exists(task.converted_filepath):
                os.remove(task.converted_filepath)
                
                
            db.session.delete(task)
            db.session.commit()
            return f'Tarea ID {id} eliminada: {task}'        

    return 'You are not logged in. <a href="/api/auth/login">Login</a> or <a href="/api/auth/register">Register</a>'

@jwt_required()
@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if 'username' in session:
        username = session['username']
        user_task_list = user_tasks.get(username, [])
        converted_file_url = None

        if request.method == 'POST':
            new_task = request.form.get('new_task')
            if new_task:
                user_task_list.append(new_task)
                user_tasks[username] = user_task_list

            if 'file' in request.files:
                file = request.files['file']

                if file.filename != '':
                    conversion_format = request.form.get('conversion_format')

                    if not conversion_format:
                        return jsonify({'error': 'Extensión de destino no especificada'}), 400

                    if not allowed_format(conversion_format):
                        return jsonify({'error': 'Extensión de destino no permitida'}), 400

                    upload_folder = app.config['UPLOAD_FOLDER']
                    os.makedirs(upload_folder, exist_ok=True)

                    filename = secure_filename(file.filename)
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    os.chmod(file_path, 0o644)

                    input_path = file_path
                    output_filename = f"converted_{filename.rsplit('.', 1)[0]}.{conversion_format}"
                    output_path = os.path.join(upload_folder, output_filename)

                    video = VideoFileClip(input_path)
                    video.write_videofile(output_path, codec='libx264')
                    os.chmod(output_path, 0o644)

                    user_task_list.append(f'Task: Convert {filename} to {conversion_format}')
                    user_tasks[username] = user_task_list

                    taskFile = FileConversionTask(
                        user_id=session['id_user'],
                        original_filename=filename,
                        original_filepath=input_path,
                        converted_filename=output_filename,
                        converted_filepath=output_path,
                        conversion_format=conversion_format,
                        status="available"
                    )
                    db.session.add(taskFile)
                    db.session.commit()

                    converted_file_url = url_for('download_file', filename=output_filename)
                    flash('Conversión exitosa', 'success')

        # Obteniendo las tareas de conversión desde la base de datos
        file_conversion_tasks = FileConversionTask.query.filter_by(user_id=session['id_user']).all()

        return render_template('tasks.html', username=username, tasks=user_task_list, converted_file_url=converted_file_url, file_conversion_tasks=file_conversion_tasks)

    return 'You are not logged in. <a href="/api/auth/login">Login</a> or <a href="/api/auth/register">Register</a>'