import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Form, Col, Row, Button, Alert, Card, Spinner } from 'react-bootstrap';

import { useAuthStore } from "@src/scripts/state";
import { createScheduling } from "@src/scripts/api";


function NewSchedulingPage() {
	const navigate = useNavigate();
	const { token } = useAuthStore();

	const [loading, setLoading] = React.useState(false);
	const [error, setError] = React.useState('');

	const [name, setName] = React.useState('');
	const [durationWeeks, setDurationWeeks] = React.useState(16);
	const [maxDailySlots, setMaxDailySlots] = React.useState(4);
	const [desiredDaysCount, setDesiredDaysCount] = React.useState(5);

	const [subjects, setSubjects] = React.useState([{ name: '' }]);
	const [groups, setGroups] = React.useState([{ name: '', subjects: [{ subject: '', lectures: 0, practices: 0 }] }]);
	const [teachers, setTeachers] = React.useState([{ name: '', subjects: [{ subject: '', is_lecturer: false, is_practitioner: false }] }]);
	const [classrooms, setClassrooms] = React.useState([{ name: '' }]);


	const availableSubjects = React.useMemo(() => {
		return subjects
			.map(s => s.name.trim())
			.filter(name => name !== '');
	}, [subjects]);

	const handleRemoveSubject = (idx) => {
		if (subjects.length <= 1) {
			setError('Має бути хоча б один предмет');
			return;
		}

		const removedSubjectName = subjects[idx].name.trim();
		
		const newSubjects = subjects.filter((_, i) => i !== idx);
		setSubjects(newSubjects);

		const newGroups = groups.map(group => ({
			...group,
			subjects: group.subjects.filter(s => s.subject !== removedSubjectName)
		}));
		setGroups(newGroups);

		const newTeachers = teachers.map(teacher => ({
			...teacher,
			subjects: teacher.subjects.filter(s => s.subject !== removedSubjectName)
		}));
		setTeachers(newTeachers);
		
		setError('');
	};

	const validateForm = () => {
		if (!name.trim()) {
			setError('Введіть назву розкладу');
			return false;
		}

		const validSubjects = subjects.filter(s => s.name.trim());
		if (validSubjects.length === 0) {
			setError('Додайте хоча б один предмет з назвою');
			return false;
		}

		const validGroups = groups.filter(g => g.name.trim());
		if (validGroups.length === 0) {
			setError('Додайте хоча б одну групу з назвою');
			return false;
		}

		for (const group of validGroups) {
			const validGroupSubjects = group.subjects.filter(s => 
				s.subject.trim() && (s.lectures > 0 || s.practices > 0)
			);
			if (validGroupSubjects.length === 0) {
				setError(`Група "${group.name}" має мати хоча б один предмет з парами`);
				return false;
			}
		}

		const validTeachers = teachers.filter(t => t.name.trim());
		if (validTeachers.length === 0) {
			setError('Додайте хоча б одного викладача з іменем');
			return false;
		}

		for (const teacher of validTeachers) {
			const validTeacherSubjects = teacher.subjects.filter(s => 
				s.subject.trim() && (s.is_lecturer || s.is_practitioner)
			);
			if (validTeacherSubjects.length === 0) {
				setError(`Викладач "${teacher.name}" має викладати хоча б один предмет`);
				return false;
			}
		}

		const validClassrooms = classrooms.filter(c => c.name.trim());
		if (validClassrooms.length === 0) {
			setError('Додайте хоча б одну аудиторію з назвою');
			return false;
		}

		return true;
	};

	const handleSubmit = async (e) => {
		e.preventDefault();
		setError('');

		if (!validateForm()) {
			return;
		}

		setLoading(true);

		const data = {
			name: name.trim(),
			duration_weeks: durationWeeks,
			max_daily_slots: maxDailySlots,
			desired_days_count: desiredDaysCount,
			subjects: subjects
				.filter(s => s.name.trim())
				.map(s => ({ name: s.name.trim() })),
			groups: groups
				.filter(g => g.name.trim())
				.map(g => ({
					name: g.name.trim(),
					subjects: g.subjects
						.filter(s => s.subject.trim() && (s.lectures > 0 || s.practices > 0))
						.map(s => ({
							subject: s.subject.trim(),
							lectures: s.lectures,
							practices: s.practices
						}))
				})),
			teachers: teachers
				.filter(t => t.name.trim())
				.map(t => ({
					name: t.name.trim(),
					subjects: t.subjects
						.filter(s => s.subject.trim() && (s.is_lecturer || s.is_practitioner))
						.map(s => ({
							subject: s.subject.trim(),
							is_lecturer: s.is_lecturer,
							is_practitioner: s.is_practitioner
						}))
				})),
			classrooms: classrooms
				.filter(c => c.name.trim())
				.map(c => ({ name: c.name.trim() })),
		};

		try {
			await createScheduling(token, data);
			navigate('/schedulings');
		} catch (err) {
			setError(err.message);
		} finally {
			setLoading(false);
		}
	};

	
	return (
		<Container className="mt-4">
			<h2 className="mb-4">Start New Scheduling</h2>
			{error && <Alert variant="danger">{error}</Alert>}

			<Form onSubmit={handleSubmit}>
				<Form.Group className="mb-3">
					<Form.Label>Scheduling Name</Form.Label>
					<Form.Control
						type="text"
						value={name}
						onChange={(e) => setName(e.target.value)}
						required
					/>
				</Form.Group>

				<Row>
					<Col md={4}>
						<Form.Group className="mb-3">
							<Form.Label>Duration (weeks)</Form.Label>
							<Form.Control
								type="number"
								value={durationWeeks}
								onChange={(e) => setDurationWeeks(parseInt(e.target.value))}
								min={1}
								required
							/>
						</Form.Group>
					</Col>
					<Col md={4}>
						<Form.Group className="mb-3">
							<Form.Label>Max daily slots</Form.Label>
							<Form.Control
								type="number"
								value={maxDailySlots}
								onChange={(e) => setMaxDailySlots(parseInt(e.target.value))}
								min={1}
								max={10}
								required
							/>
						</Form.Group>
					</Col>
					<Col md={4}>
						<Form.Group className="mb-3">
							<Form.Label>Desired days per week</Form.Label>
							<Form.Control
								type="number"
								value={desiredDaysCount}
								onChange={(e) => setDesiredDaysCount(parseInt(e.target.value))}
								min={1}
								max={7}
								required
							/>
						</Form.Group>
					</Col>
				</Row>

				<Card className="mb-3">
					<Card.Body>
						<Card.Title>Subjects</Card.Title>
						{subjects.map((subj, idx) => (
							<div key={idx} className="mb-2 d-flex gap-2">
								<Form.Control
									type="text"
									placeholder="Subject name"
									value={subj.name}
									onChange={(e) => {
										const newSubjects = [...subjects];
										newSubjects[idx].name = e.target.value;
										setSubjects(newSubjects);
									}}
								/>
								<Button 
									variant="danger" 
									onClick={() => handleRemoveSubject(idx)}
									disabled={subjects.length <= 1}
								>
									Remove
								</Button>
							</div>
						))}
						<Button variant="secondary" onClick={() => setSubjects([...subjects, { name: '' }])}>
							Add Subject
						</Button>
					</Card.Body>
				</Card>

				<Card className="mb-3">
					<Card.Body>
						<Card.Title>Groups</Card.Title>
						{groups.map((group, gIdx) => (
							<Card key={gIdx} className="mb-3">
								<Card.Body>
									<Form.Group className="mb-2">
										<Form.Label>Group Name</Form.Label>
										<Form.Control
											type="text"
											value={group.name}
											onChange={(e) => {
												const newGroups = [...groups];
												newGroups[gIdx].name = e.target.value;
												setGroups(newGroups);
											}}
										/>
									</Form.Group>
									{group.subjects.map((subj, sIdx) => {
										const usedSubjectsInGroup = group.subjects
											.map((s, idx) => idx !== sIdx ? s.subject : null)
											.filter(Boolean);
										
										return (
											<div key={sIdx} className="mb-2">
												<Row>
													<Col md={4}>
														<Form.Label>Subject</Form.Label>
														<Form.Select
															value={subj.subject}
															onChange={(e) => {
																const newGroups = [...groups];
																newGroups[gIdx].subjects[sIdx].subject = e.target.value;
																setGroups(newGroups);
															}}
														>
															<option value="">Select subject</option>
															{availableSubjects.map((subjName, i) => (
																<option 
																	key={i} 
																	value={subjName}
																	disabled={usedSubjectsInGroup.includes(subjName)}
																>
																	{subjName}
																</option>
															))}
														</Form.Select>
													</Col>
												<Col md={3}>
													<Form.Label>Lectures</Form.Label>
													<Form.Control
														type="number"
														placeholder="0"
														value={subj.lectures}
														onChange={(e) => {
															const newGroups = [...groups];
															newGroups[gIdx].subjects[sIdx].lectures = parseInt(e.target.value) || 0;
															setGroups(newGroups);
														}}
														min={0}
													/>
												</Col>
												<Col md={3}>
													<Form.Label>Practices</Form.Label>
													<Form.Control
														type="number"
														placeholder="0"
														value={subj.practices}
														onChange={(e) => {
															const newGroups = [...groups];
															newGroups[gIdx].subjects[sIdx].practices = parseInt(e.target.value) || 0;
															setGroups(newGroups);
														}}
														min={0}
													/>
												</Col>
												<Col md={2}>
													<Form.Label>&nbsp;</Form.Label>
													<Button 
														variant="danger" 
														size="sm"
														className="w-100"
														onClick={() => {
															const newGroups = [...groups];
															newGroups[gIdx].subjects = newGroups[gIdx].subjects.filter((_, i) => i !== sIdx);
															setGroups(newGroups);
														}}
														disabled={group.subjects.length <= 1}
													>
														Remove
													</Button>
												</Col>
											</Row>
										</div>
									);
									})}
									<Button 
										variant="secondary" 
										size="sm"
										onClick={() => {
											const newGroups = [...groups];
											newGroups[gIdx].subjects.push({ subject: '', lectures: 0, practices: 0 });
											setGroups(newGroups);
										}}
										disabled={availableSubjects.length === 0}
									>
										Add Subject to Group
									</Button>
									<Button 
										variant="danger" 
										size="sm"
										className="ms-2"
										onClick={() => setGroups(groups.filter((_, i) => i !== gIdx))}
										disabled={groups.length <= 1}
									>
										Remove Group
									</Button>
								</Card.Body>
							</Card>
						))}
						<Button variant="secondary" onClick={() => setGroups([...groups, { name: '', subjects: [{ subject: '', lectures: 0, practices: 0 }] }])}>
							Add Group
						</Button>
					</Card.Body>
				</Card>

				<Card className="mb-3">
					<Card.Body>
						<Card.Title>Teachers</Card.Title>
						{teachers.map((teacher, tIdx) => (
							<Card key={tIdx} className="mb-3">
								<Card.Body>
									<Form.Group className="mb-2">
										<Form.Label>Teacher Name</Form.Label>
										<Form.Control
											type="text"
											value={teacher.name}
											onChange={(e) => {
												const newTeachers = [...teachers];
												newTeachers[tIdx].name = e.target.value;
												setTeachers(newTeachers);
											}}
										/>
									</Form.Group>
									{teacher.subjects.map((subj, sIdx) => {
										const usedSubjectsInTeacher = teacher.subjects
											.map((s, idx) => idx !== sIdx ? s.subject : null)
											.filter(Boolean);
										
										return (
											<div key={sIdx} className="mb-3">
												<Row>
													<Col md={4}>
														<Form.Label>Subject</Form.Label>
														<Form.Select
															value={subj.subject}
															onChange={(e) => {
																const newTeachers = [...teachers];
																newTeachers[tIdx].subjects[sIdx].subject = e.target.value;
																setTeachers(newTeachers);
															}}
														>
															<option value="">Select subject</option>
															{availableSubjects.map((subjName, i) => (
																<option 
																	key={i} 
																	value={subjName}
																	disabled={usedSubjectsInTeacher.includes(subjName)}
																>
																	{subjName}
																</option>
															))}
														</Form.Select>
													</Col>
												<Col md={3}>
													<Form.Label>Can teach as</Form.Label>
													<div>
														<Form.Check
															type="checkbox"
															label="Lecturer"
															checked={subj.is_lecturer}
															onChange={(e) => {
																const newTeachers = [...teachers];
																newTeachers[tIdx].subjects[sIdx].is_lecturer = e.target.checked;
																setTeachers(newTeachers);
															}}
														/>
														<Form.Check
															type="checkbox"
															label="Practitioner"
															checked={subj.is_practitioner}
															onChange={(e) => {
																const newTeachers = [...teachers];
																newTeachers[tIdx].subjects[sIdx].is_practitioner = e.target.checked;
																setTeachers(newTeachers);
															}}
														/>
													</div>
												</Col>
												<Col md={2}>
													<Form.Label>&nbsp;</Form.Label>
													<Button 
														variant="danger"
														size="sm"
														className="w-100"
														onClick={() => {
															const newTeachers = [...teachers];
															newTeachers[tIdx].subjects = newTeachers[tIdx].subjects.filter((_, i) => i !== sIdx);
															setTeachers(newTeachers);
														}}
														disabled={teacher.subjects.length <= 1}
													>
														Remove
													</Button>
												</Col>
											</Row>
										</div>
									);
									})}
									<Button 
										variant="secondary"
										size="sm"
										onClick={() => {
											const newTeachers = [...teachers];
											newTeachers[tIdx].subjects.push({ subject: '', is_lecturer: false, is_practitioner: false });
											setTeachers(newTeachers);
										}}
										disabled={availableSubjects.length === 0}
									>
										Add Subject to Teacher
									</Button>
									<Button 
										variant="danger"
										size="sm"
										className="ms-2"
										onClick={() => setTeachers(teachers.filter((_, i) => i !== tIdx))}
										disabled={teachers.length <= 1}
									>
										Remove Teacher
									</Button>
								</Card.Body>
							</Card>
						))}
						<Button variant="secondary" onClick={() => setTeachers([...teachers, { name: '', subjects: [{ subject: '', is_lecturer: false, is_practitioner: false }] }])}>
							Add Teacher
						</Button>
					</Card.Body>
				</Card>

				<Card className="mb-3">
					<Card.Body>
						<Card.Title>Classrooms</Card.Title>
						{classrooms.map((room, idx) => (
							<div key={idx} className="mb-2 d-flex gap-2">
								<Form.Control
									type="text"
									placeholder="Classroom name"
									value={room.name}
									onChange={(e) => {
										const newClassrooms = [...classrooms];
										newClassrooms[idx].name = e.target.value;
										setClassrooms(newClassrooms);
									}}
								/>
								<Button 
									variant="danger"
									onClick={() => setClassrooms(classrooms.filter((_, i) => i !== idx))}
									disabled={classrooms.length <= 1}
								>
									Remove
								</Button>
							</div>
						))}
						<Button variant="secondary" onClick={() => setClassrooms([...classrooms, { name: '' }])}>
							Add Classroom
						</Button>
					</Card.Body>
				</Card>

				<div className="d-flex gap-2">
					<Button variant="primary" type="submit" disabled={loading}>
						{loading ? <Spinner size="sm" animation="border" /> : 'Start'}
					</Button>
					<Button variant="secondary" onClick={() => navigate('/schedulings')}>
						Cancel
					</Button>
				</div>
			</Form>
		</Container>
	);
}


export { NewSchedulingPage };